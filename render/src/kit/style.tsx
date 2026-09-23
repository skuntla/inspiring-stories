import React from 'react';
import type {Palette, TimeOfDay} from './types';

/** The one ink outline used on every shape in every component. */
export const INK = '#3b2a20';
export const ink = (width = 3, opacity = 1) => ({
	stroke: INK,
	strokeWidth: width,
	strokeLinejoin: 'round' as const,
	strokeLinecap: 'round' as const,
	strokeOpacity: opacity,
});

/** Deterministic pseudo-random in [0, 1) for scattering grass, stones and particles. */
export const rand = (i: number, salt = 0) => {
	const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
	return x - Math.floor(x);
};

export const ease = (x: number) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);

const PALETTES: Record<TimeOfDay, Palette> = {
	dawn: {skyTop: '#9fb3cf', skyMid: '#f1c9a8', skyBottom: '#f6b27a', sun: '#ffe2a8', sunX: 0.78, sunY: 0.55,
		tint: '#f3a46a', tintOpacity: 0.1, light: 0.6},
	morning: {skyTop: '#c9d6dc', skyMid: '#e9e3cf', skyBottom: '#f1e6c9', sun: '#fff6dc', sunX: 0.72, sunY: 0.22,
		tint: '#fff3d6', tintOpacity: 0.04, light: 0.85},
	midday: {skyTop: '#8fc1e3', skyMid: '#c7e3f0', skyBottom: '#eef5ee', sun: '#fffbe8', sunX: 0.55, sunY: 0.1,
		tint: '#ffffff', tintOpacity: 0, light: 1},
	afternoon: {skyTop: '#9ab8d6', skyMid: '#e8d9b6', skyBottom: '#f0d7a4', sun: '#ffe7b0', sunX: 0.3, sunY: 0.25,
		tint: '#f5c77e', tintOpacity: 0.07, light: 0.9},
	dusk: {skyTop: '#5f6f9c', skyMid: '#e8a172', skyBottom: '#f28a55', sun: '#ffc27a', sunX: 0.2, sunY: 0.5,
		tint: '#e7835a', tintOpacity: 0.16, light: 0.5},
	night: {skyTop: '#141d33', skyMid: '#26345a', skyBottom: '#3a4a6e', sun: '#e8edf8', sunX: 0.78, sunY: 0.16,
		tint: '#1c2848', tintOpacity: 0.42, light: 0.2},
};

export const palette = (timeOfDay: TimeOfDay): Palette => PALETTES[timeOfDay];

/** Sky gradient and sun (or moon) glow for outdoor locations. */
export const Sky: React.FC<{palette: Palette}> = ({palette: p}) => (
	<g>
		<rect x={-200} y={-200} width={2320} height={1480} fill="url(#sky)" />
		<circle cx={p.sunX * 1920} cy={p.sunY * 1080} r={260} fill="url(#sunGlow)" />
		<circle cx={p.sunX * 1920} cy={p.sunY * 1080} r={48} fill={p.sun} opacity={0.9} />
	</g>
);

/** Shared SVG definitions: sky gradient, glows, watercolor and paper filters, vignette. */
export const Defs: React.FC<{palette: Palette}> = ({palette: p}) => (
	<defs>
		<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stopColor={p.skyTop} />
			<stop offset="0.6" stopColor={p.skyMid} />
			<stop offset="1" stopColor={p.skyBottom} />
		</linearGradient>
		<radialGradient id="sunGlow">
			<stop offset="0" stopColor={p.sun} stopOpacity={0.8} />
			<stop offset="1" stopColor={p.sun} stopOpacity={0} />
		</radialGradient>
		<radialGradient id="warmGlow">
			<stop offset="0" stopColor="#ffcf7a" stopOpacity={0.75} />
			<stop offset="1" stopColor="#ffb14a" stopOpacity={0} />
		</radialGradient>
		<radialGradient id="vignette" cx="0.5" cy="0.5" r="0.75">
			<stop offset="0.6" stopColor="#000" stopOpacity={0} />
			<stop offset="1" stopColor="#2a2418" stopOpacity={0.35} />
		</radialGradient>
		{/* watercolor: wobbly edges and a slight bleed; use on static background layers only (it is slow) */}
		<filter id="watercolor" x="-5%" y="-5%" width="110%" height="110%">
			<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves={3} seed={7} result="noise" />
			<feDisplacementMap in="SourceGraphic" in2="noise" scale={12} xChannelSelector="R" yChannelSelector="G" result="w" />
			<feGaussianBlur in="w" stdDeviation={1} />
		</filter>
		{/* softEdge: a light hand-drawn wobble for characters and props */}
		<filter id="softEdge" x="-10%" y="-10%" width="120%" height="120%">
			<feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves={2} seed={3} result="noise" />
			<feDisplacementMap in="SourceGraphic" in2="noise" scale={3} xChannelSelector="R" yChannelSelector="G" />
		</filter>
		<filter id="blur8"><feGaussianBlur stdDeviation={8} /></filter>
		<filter id="blur30" x="-30%" y="-100%" width="160%" height="300%"><feGaussianBlur stdDeviation={30} /></filter>
		<filter id="farBlur"><feGaussianBlur stdDeviation={2} /></filter>
		<filter id="paper" x="0" y="0" width="100%" height="100%">
			<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={3} seed={11} />
			<feColorMatrix type="saturate" values="0" />
		</filter>
	</defs>
);
