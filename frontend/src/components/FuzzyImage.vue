<template>
    <canvas ref="canvasRef" :class="className" />
</template>

<script setup>
import { onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue';

const props = defineProps({
    src: { type: String, required: true },
    enableHover: { type: Boolean, default: true },
    baseIntensity: { type: Number, default: 0.18 },
    hoverIntensity: { type: Number, default: 0.5 },
    fuzzRange: { type: Number, default: 30 },
    fps: { type: Number, default: 60 },
    direction: { type: String, default: 'horizontal' }, // 'horizontal' | 'vertical' | 'both'
    transitionDuration: { type: Number, default: 0 },
    clickEffect: { type: Boolean, default: false },
    glitchMode: { type: Boolean, default: false },
    glitchInterval: { type: Number, default: 2000 },
    glitchDuration: { type: Number, default: 200 },
    className: { type: String, default: '' }
});

const canvasRef = useTemplateRef('canvasRef');

let animationFrameId;
let glitchTimeoutId;
let glitchEndTimeoutId;
let clickTimeoutId;
let cancelled = false;

const init = () => {
    const canvas = canvasRef.value;
    if (!canvas) return;

    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) return;

    const img = new Image();
    img.src = props.src;

    img.onload = () => {
        if (cancelled) return;

        const offscreen = document.createElement('canvas');
        const offCtx = offscreen.getContext('2d', { willReadFrequently: true });

        // Draw the original image onto the offscreen canvas
        offscreen.width = img.naturalWidth;
        offscreen.height = img.naturalHeight;
        offCtx.drawImage(img, 0, 0);

        const marginX = props.fuzzRange + 20;
        const marginY = props.direction === 'vertical' || props.direction === 'both' ? props.fuzzRange + 10 : 0;

        // Adjust main canvas size to include margins for the fuzzy bleed effect
        canvas.width = offscreen.width + marginX * 2;
        canvas.height = offscreen.height + marginY * 2;
        ctx.translate(marginX, marginY);

        let isHovering = false;
        let isClicking = false;
        let isGlitching = false;
        let currentIntensity = props.baseIntensity;
        let targetIntensity = props.baseIntensity;
        let lastFrameTime = 0;
        const frameDuration = 1000 / props.fps;

        const startGlitch = () => {
            if (!props.glitchMode || cancelled) return;
            glitchTimeoutId = setTimeout(() => {
                isGlitching = true;
                glitchEndTimeoutId = setTimeout(() => {
                    isGlitching = false;
                    startGlitch();
                }, props.glitchDuration);
            }, props.glitchInterval);
        };

        if (props.glitchMode) startGlitch();

        const run = (ts) => {
            if (cancelled) return;

            if (ts - lastFrameTime < frameDuration) {
                animationFrameId = requestAnimationFrame(run);
                return;
            }

            lastFrameTime = ts;

            // Clear the canvas taking translation into account
            ctx.clearRect(-marginX, -marginY, canvas.width, canvas.height);

            targetIntensity = isClicking || isGlitching ? 1 : isHovering ? props.hoverIntensity : props.baseIntensity;

            if (props.transitionDuration > 0) {
                const step = 1 / (props.transitionDuration / frameDuration);
                currentIntensity += Math.sign(targetIntensity - currentIntensity) * step;
                currentIntensity = Math.min(
                    Math.max(currentIntensity, Math.min(targetIntensity, currentIntensity)),
                    Math.max(targetIntensity, currentIntensity)
                );
            } else {
                currentIntensity = targetIntensity;
            }

            // Slice the offscreen canvas strip by strip and draw it with fuzz offset
            for (let y = 0; y < offscreen.height; y++) {
                const dx = props.direction !== 'vertical' ? (Math.random() - 0.5) * currentIntensity * props.fuzzRange : 0;
                const dy = props.direction !== 'horizontal' ? (Math.random() - 0.5) * currentIntensity * props.fuzzRange * 0.5 : 0;

                ctx.drawImage(offscreen, 0, y, offscreen.width, 1, dx, y + dy, offscreen.width, 1);
            }

            animationFrameId = requestAnimationFrame(run);
        };

        animationFrameId = requestAnimationFrame(run);

        const rectCheck = (x, y) =>
            x >= marginX && x <= marginX + offscreen.width && y >= marginY && y <= marginY + offscreen.height;

        const mouseMove = (e) => {
            if (!props.enableHover) return;
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            isHovering = rectCheck((e.clientX - rect.left) * scaleX, (e.clientY - rect.top) * scaleY);
        };

        const mouseLeave = () => (isHovering = false);

        const click = () => {
            if (!props.clickEffect) return;
            isClicking = true;
            clearTimeout(clickTimeoutId);
            clickTimeoutId = setTimeout(() => (isClicking = false), 150);
        };

        if (props.enableHover) {
            canvas.addEventListener('mousemove', mouseMove);
            canvas.addEventListener('mouseleave', mouseLeave);
        }

        if (props.clickEffect) {
            canvas.addEventListener('click', click);
        }

        canvas._cleanup = () => {
            cancelAnimationFrame(animationFrameId);
            clearTimeout(glitchTimeoutId);
            clearTimeout(glitchEndTimeoutId);
            clearTimeout(clickTimeoutId);
            canvas.removeEventListener('mousemove', mouseMove);
            canvas.removeEventListener('mouseleave', mouseLeave);
            canvas.removeEventListener('click', click);
        };
    };
};

onMounted(init);

onBeforeUnmount(() => {
    cancelled = true;
    if (canvasRef.value && canvasRef.value._cleanup) {
        canvasRef.value._cleanup();
    }
});

watch(
    () => ({ ...props }),
    () => {
        cancelled = true;
        if (canvasRef.value && canvasRef.value._cleanup) {
            canvasRef.value._cleanup();
        }
        cancelled = false;
        init();
    }
);
</script>
