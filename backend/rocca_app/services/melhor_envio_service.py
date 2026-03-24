"""
Serviço de integração com a API da Melhor Envio.
Responsável por cálculo de frete e futura geração de etiquetas.

Princípios:
- Tokens são persistidos no banco (AppSetting) para sobreviver a restarts
- Retry automático quando token expira (HTTP 401)
- Validações de dimensões mínimas/máximas dos Correios
- Nunca confiar em dados vindos do frontend
"""
import os
import requests
import re


class MelhorEnvioError(Exception):
    """Exceção base para erros da Melhor Envio."""
    def __init__(self, message, status_code=None, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class MelhorEnvioService:
    """
    Camada de serviço para a API da Melhor Envio.
    
    Uso:
        service = MelhorEnvioService()
        opcoes = service.calculate_shipping("01001000", products_data)
    """

    # Limites físicos dos Correios
    MIN_WEIGHT = 0.3       # 300g mínimo
    MAX_WEIGHT = 30.0      # 30kg máximo
    MIN_LENGTH = 16.0      # cm
    MIN_WIDTH = 11.0       # cm
    MIN_HEIGHT = 2.0       # cm
    MAX_DIMENSION = 105.0  # cm (por dimensão individual)
    MAX_SUM_DIMENSIONS = 200.0  # cm (soma L+A+C)

    # Serviços disponíveis: Correios + Jadlog
    # 1 = PAC, 2 = SEDEX, 3 = Jadlog .Package, 4 = Jadlog .Com
    ALLOWED_SERVICE_IDS = [1, 2]

    def __init__(self):
        self.client_id = os.environ.get("ME_CLIENT_ID", "")
        self.client_secret = os.environ.get("ME_CLIENT_SECRET", "")
        self.environment = os.environ.get("ME_ENVIRONMENT", "sandbox")
        self.cep_origem = os.environ.get("ME_CEP_ORIGEM", "01001000")
        
        # Token: primeiro tenta do banco (AppSetting), depois do .env como fallback
        self._access_token = None
        self._refresh_token_value = None

    def _load_tokens(self):
        """
        Carrega tokens do banco de dados (AppSetting).
        Se não existir no banco (ou DB inacessível), usa o .env como fallback.
        """
        from ..models import AppSetting
        
        try:
            db_access = AppSetting.get_value("me_access_token")
            db_refresh = AppSetting.get_value("me_refresh_token")
        except Exception as e:
            print(f"[MelhorEnvio] Aviso: erro ao acessar banco para tokens ({e}). Usando .env como fallback.")
            db_access = None
            db_refresh = None
        
        if db_access:
            self._access_token = db_access
            self._refresh_token_value = db_refresh or os.environ.get("ME_REFRESH_TOKEN", "")
        else:
            # Fallback: usa .env (primeira vez antes de qualquer refresh, ou DB inacessível)
            self._access_token = os.environ.get("ME_ACCESS_TOKEN", "")
            self._refresh_token_value = os.environ.get("ME_REFRESH_TOKEN", "")

    @property
    def access_token(self):
        if self._access_token is None:
            self._load_tokens()
        return self._access_token

    @property
    def refresh_token_val(self):
        if self._refresh_token_value is None:
            self._load_tokens()
        return self._refresh_token_value

    def _get_base_url(self):
        """Retorna URL base de acordo com o ambiente (sandbox ou produção)."""
        if self.environment == "production":
            return "https://melhorenvio.com.br"
        return "https://sandbox.melhorenvio.com.br"

    def _get_headers(self):
        """Monta headers de autenticação."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": os.environ.get("ME_USER_AGENT", "E-Commerce App (contato@example.com)")
        }

    def _refresh_token(self):
        """
        Renova o access_token usando o refresh_token.
        Chamado automaticamente quando recebemos 401 (Unauthorized).
        
        O novo token é salvo no banco (AppSetting) para persistir
        entre restarts do servidor.
        """
        from ..models import AppSetting
        
        if not self.refresh_token_val:
            raise MelhorEnvioError(
                "Token expirado e nenhum refresh_token disponível. "
                "Reautorize manualmente no painel da Melhor Envio.",
                status_code=401
            )
        
        url = f"{self._get_base_url()}/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token_val,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=15)
            
            if response.status_code == 401 or response.status_code == 400:
                raise MelhorEnvioError(
                    "Refresh token inválido ou expirado (validade: 45 dias). "
                    "Acesse o painel da Melhor Envio para gerar novo token.",
                    status_code=401
                )
            
            response.raise_for_status()
            data = response.json()
            
            new_access = data.get("access_token")
            new_refresh = data.get("refresh_token", self.refresh_token_val)
            
            if not new_access:
                raise MelhorEnvioError(
                    "Resposta de refresh não contém access_token.",
                    status_code=500
                )
            
            # Atualiza em memória
            self._access_token = new_access
            self._refresh_token_value = new_refresh
            
            # Persiste no banco para sobreviver a restarts
            AppSetting.set_value("me_access_token", new_access)
            AppSetting.set_value("me_refresh_token", new_refresh)
            
            print("[MelhorEnvio] Token renovado e salvo no banco com sucesso.")
            return True
            
        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                raise  # Já tratado acima
            print(f"[MelhorEnvio] ERRO de conexão ao renovar token: {e}")
            raise MelhorEnvioError(
                "Erro de conexão ao renovar token da Melhor Envio.",
                status_code=503
            )

    def _validate_cep(self, cep):
        """
        Valida e limpa o CEP.
        Retorna CEP limpo (8 dígitos) ou levanta erro.
        """
        cep = re.sub(r'[^0-9]', '', str(cep).strip())
        
        if len(cep) != 8:
            raise MelhorEnvioError(
                f"CEP inválido: '{cep}'. Informe exatamente 8 dígitos.",
                status_code=400
            )
        
        return cep

    def _aggregate_dimensions(self, products_data):
        """
        Calcula peso total e dimensões do pacote para envio.
        
        products_data: lista de dicts com:
            {
                "weight": float,     # peso em KG
                "width": float,      # largura em CM
                "height": float,     # altura em CM
                "length": float,     # comprimento em CM
                "quantity": int
            }
        
        Estratégia:
        - Peso: soma de (peso_unitário × quantidade)
        - Comprimento e Largura: maior valor entre os produtos
        - Altura: soma das alturas (empilhado)
        
        Aplica limites mínimos e máximos dos Correios.
        """
        total_weight = 0.0
        max_length = 0.0
        max_width = 0.0
        total_height = 0.0

        for prod in products_data:
            qty = prod.get("quantity", 1)
            
            # Se peso é 0, usa default de 0.3kg (evita erro 422 da API)
            weight = float(prod.get("weight", 0)) or 0.3
            length = float(prod.get("length", 0)) or self.MIN_LENGTH
            width = float(prod.get("width", 0)) or self.MIN_WIDTH
            height = float(prod.get("height", 0)) or self.MIN_HEIGHT
            
            total_weight += weight * qty
            max_length = max(max_length, length)
            max_width = max(max_width, width)
            total_height += height * qty

        # Aplica mínimos dos Correios
        total_weight = max(total_weight, self.MIN_WEIGHT)
        max_length = max(max_length, self.MIN_LENGTH)
        max_width = max(max_width, self.MIN_WIDTH)
        total_height = max(total_height, self.MIN_HEIGHT)

        # Aplica máximos dos Correios
        if total_weight > self.MAX_WEIGHT:
            raise MelhorEnvioError(
                f"Peso total ({total_weight:.1f}kg) excede o limite dos Correios ({self.MAX_WEIGHT}kg). "
                "Considere dividir em múltiplos envios.",
                status_code=400
            )
        
        max_length = min(max_length, self.MAX_DIMENSION)
        max_width = min(max_width, self.MAX_DIMENSION)
        total_height = min(total_height, self.MAX_DIMENSION)
        
        soma_dimensoes = max_length + max_width + total_height
        if soma_dimensoes > self.MAX_SUM_DIMENSIONS:
            raise MelhorEnvioError(
                f"Soma das dimensões ({soma_dimensoes:.0f}cm) excede o limite dos Correios ({self.MAX_SUM_DIMENSIONS}cm). "
                "Considere dividir em múltiplos envios.",
                status_code=400
            )

        return {
            "weight": round(total_weight, 2),
            "width": round(max_width, 2),
            "height": round(total_height, 2),
            "length": round(max_length, 2),
        }

    def calculate_shipping(self, cep_destino, products_data):
        """
        Calcula opções de frete.
        
        Args:
            cep_destino (str): CEP do cliente (apenas números ou com hífen)
            products_data (list): Lista de produtos com peso e dimensões
            
        Returns:
            list: Opções de frete disponíveis, cada uma com:
                - id (int): ID do serviço
                - name (str): Nome do serviço (ex: "PAC")
                - price (float): Preço do frete
                - delivery_time (int): Prazo em dias úteis
                - company_name (str): Nome da transportadora
                
        Raises:
            MelhorEnvioError: Em caso de erro na API ou validação
        """
        cep_destino = self._validate_cep(cep_destino)
        
        if not products_data:
            raise MelhorEnvioError("Nenhum produto informado para cálculo.", status_code=400)

        dimensions = self._aggregate_dimensions(products_data)

        url = f"{self._get_base_url()}/api/v2/me/shipment/calculate"
        payload = {
            "from": {"postal_code": self.cep_origem},
            "to": {"postal_code": cep_destino},
            "products": [
                {
                    "id": "package",
                    "width": dimensions["width"],
                    "height": dimensions["height"],
                    "length": dimensions["length"],
                    "weight": dimensions["weight"],
                    "insurance_value": 0,
                    "quantity": 1,
                }
            ],
            "services": ",".join(str(s) for s in self.ALLOWED_SERVICE_IDS),
        }

        return self._make_request(url, payload)

    def _make_request(self, url, payload, retry_on_401=True):
        """
        Faz requisição HTTP com retry automático para token expirado.
        """
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )

            # Token expirado → tenta renovar e refazer
            if response.status_code == 401 and retry_on_401:
                print("[MelhorEnvio] Token expirado (401), tentando renovar...")
                self._refresh_token()
                return self._make_request(url, payload, retry_on_401=False)

            if response.status_code == 422:
                errors = response.json()
                print(f"[MelhorEnvio] Erro 422: {errors}")
                raise MelhorEnvioError(
                    "Dados inválidos enviados à Melhor Envio. "
                    "Verifique peso e dimensões dos produtos.",
                    status_code=422,
                    details=errors
                )

            response.raise_for_status()
            data = response.json()

            # Filtra e formata as opções válidas

            options = []
            for service in data:
                # Serviços com erro são ignorados (ex: rota não atendida)
                if service.get("error"):
                    print(f"[MelhorEnvio] Serviço {service.get('name', '?')} indisponível: {service.get('error')}")
                    continue
                
                price = service.get("price") or service.get("custom_price")
                if not price:
                    continue
                    
                options.append({
                    "id": service.get("id"),
                    "name": service.get("name", ""),
                    "price": float(price),
                    "delivery_time": int(service.get("delivery_time", 0)),
                    "company_name": service.get("company", {}).get("name", ""),
                    "company_picture": service.get("company", {}).get("picture", ""),
                })

            if not options:
                raise MelhorEnvioError(
                    "Nenhuma opção de frete disponível para este CEP. "
                    "Verifique se o CEP está correto.",
                    status_code=404
                )

            # Ordena por preço (mais barato primeiro)
            options.sort(key=lambda x: x["price"])

            return options

        except MelhorEnvioError:
            raise  # Re-levanta erros já tratados
        except requests.exceptions.Timeout:
            raise MelhorEnvioError(
                "Timeout ao consultar Melhor Envio. Tente novamente em instantes.",
                status_code=504
            )
        except requests.exceptions.ConnectionError:
            raise MelhorEnvioError(
                "Erro de conexão com a Melhor Envio. Tente novamente.",
                status_code=503
            )
        except Exception as e:
            print(f"[MelhorEnvio] Erro inesperado: {e}")
            raise MelhorEnvioError(
                "Erro interno ao processar cálculo de frete.",
                status_code=500
            )

    # ============================================================
    # PREPARAÇÃO FUTURA: Geração de Etiqueta (NÃO implementado)
    # ============================================================
    # Fluxo futuro:
    # 1. POST /api/v2/me/cart         → adicionar envio ao carrinho ME
    # 2. POST /api/v2/me/shipment/checkout  → comprar o frete
    # 3. POST /api/v2/me/shipment/generate  → gerar etiqueta
    # 4. GET  /api/v2/me/shipment/print     → baixar PDF da etiqueta
    #
    # Por enquanto, o admin faz esses passos manualmente no painel
    # da Melhor Envio (melhorenvio.com.br).
    # ============================================================
