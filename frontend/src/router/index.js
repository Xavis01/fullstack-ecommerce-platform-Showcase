import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import ProductsView from '@/views/ProductsView.vue'
import ProductDetailView from '@/views/ProductDetailView.vue'
import CartView from '@/views/CartView.vue'
import ArchiveView from '@/views/ArchiveView.vue'
import AdminProductsView from '@/views/admin/AdminProductsView.vue'
import AdminBinProductsView from '../views/admin/AdminBinProductsView.vue'

// ─── Helper: lê o claim is_admin do JWT no localStorage ──────────────────────
function getIsAdminFromToken() {
  try {
    const token = localStorage.getItem('token')
    if (!token) return false
    // JWT: header.payload.signature — decodifica apenas o payload (base64)
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload?.is_admin === true
  } catch {
    return false
  }
}
// ─────────────────────────────────────────────────────────────────────────────

const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/produtos', name: 'Produtos', component: ProductsView },
  { path: '/produto/:id', name: 'ProdutoDetalhado', component: ProductDetailView },
  { path: '/cart', name: 'Cart', component: CartView },
  { path: '/checkout', name: 'Checkout', component: () => import('@/views/CheckoutView.vue') },
  { path: '/checkout/sucesso', name: 'CheckoutSuccess', component: () => import('@/views/OrderSuccessView.vue') },
  { path: '/checkout/pix', name: 'CheckoutPix', component: () => import('@/views/OrderPendingPixView.vue') },
  { path: '/archive', name: 'Archive', component: ArchiveView },

  // Rotas do Usuário
  { path: '/meus-pedidos', name: 'UserPedidos', component: () => import('@/views/user/UserOrdersView.vue') },
  { path: '/minha-conta', name: 'UserConta', component: () => import('@/views/user/UserProfileView.vue') },

  // modal será mostrado ao acessar essa rota
  { path: '/admin', name: 'AdminSidebar', component: HomeView, meta: { requiresAdmin: true } },

  // Rotas admin — todas protegidas
  { path: '/admin/produtos', name: 'AdminProdutos', component: AdminProductsView, meta: { requiresAdmin: true } },
  { path: '/admin/produtos/lixeira', name: 'AdminBinProdutos', component: AdminBinProductsView, meta: { requiresAdmin: true } },
  { path: '/admin/categorias', name: 'AdminCategorias', component: () => import('@/views/admin/AdminCategoriesView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/pedidos', name: 'AdminPedidos', component: () => import('@/views/admin/AdminOrdersView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/precificacao', name: 'AdminPricing', component: () => import('@/views/admin/AdminPricingView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/venda-rapida', name: 'AdminFastSale', component: () => import('@/views/admin/AdminFastSaleView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/usuarios', name: 'AdminUsuarios', component: () => import('@/views/admin/AdminUsersView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/colecoes', name: 'AdminColecoes', component: () => import('@/views/admin/AdminCollectionsView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/cupons', name: 'AdminCupons', component: () => import('@/views/admin/AdminCouponsView.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/frete', name: 'AdminFrete', component: () => import('@/views/admin/AdminShippingView.vue'), meta: { requiresAdmin: true } },
  
  // Páginas institucionais
  { path: '/politica-de-troca', name: 'ReturnPolicy', component: () => import('@/views/ReturnPolicyView.vue') },
  { path: '/politica-de-privacidade', name: 'PrivacyPolicy', component: () => import('@/views/PrivacyPolicyView.vue') },

  // 404 - Deve ser a última!
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('@/views/NotFoundView.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// ─── Guard global: redireciona não-admins para Home ───────────────────────────
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAdmin) {
    if (!getIsAdminFromToken()) {
      // Não é admin (ou não está logado): manda para Home silenciosamente
      return next({ name: 'Home' })
    }
  }
  next()
})
// ─────────────────────────────────────────────────────────────────────────────

export default router
