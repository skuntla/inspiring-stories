import React from 'react';
import {rand} from './style';
import type {Palette} from './types';

// One overlay per atmosphere value in the vocabulary. Each draws in the scene's 1920x1080 space,
// in a back layer (behind characters) and/or a front layer (over them). All motion is a pure
// function of t, so every frame renders the same way every time.

type P = {t: number; palette: Palette; layer: 'back' | 'front'};
const W = 1920;
const H = 1080;
const loop = (v: number, span: number) => ((v % span) + span) % span;

const Fog: React.FC<P> = ({t, layer}) =>
	layer === 'back' ? (
		<g filter="url(#blur30)" opacity={0.7}>
			<ellipse cx={loop(300 + t * 16, 2600) - 300} cy={640} rx={720} ry={95} fill="#f2efe8" opacity={0.75} />
			<ellipse cx={loop(1500 - t * 11, 2600) - 300} cy={560} rx={820} ry={120} fill="#f2efe8" opacity={0.6} />
			<ellipse cx={960 + Math.sin(t * 0.35) * 220} cy={760} rx={1150} ry={80} fill="#f2efe8" opacity={0.5} />
		</g>
	) : (
		<g filter="url(#blur30)" opacity={0.35}>
			<ellipse cx={700 + Math.sin(t * 0.45) * 180} cy={980} rx={760} ry={45} fill="#f4f1ea" />
		</g>
	);

const Mist: React.FC<P> = ({t, layer}) =>
	layer === 'back' ? (
		<g filter="url(#blur30)" opacity={0.45}>
			<ellipse cx={loop(600 + t * 10, 2600) - 300} cy={760} rx={900} ry={60} fill="#f4f2ec" />
			<ellipse cx={loop(1700 - t * 8, 2600) - 300} cy={700} rx={700} ry={50} fill="#f4f2ec" />
		</g>
	) : null;

const Rain: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g stroke="#c8d4e0" strokeWidth={2} strokeLinecap="round" opacity={0.55}>
			{Array.from({length: 150}).map((_, i) => {
				const x = rand(i, 1) * (W + 300) - 150;
				const y = loop(rand(i, 2) * H + t * (900 + rand(i, 3) * 300), H + 100) - 50;
				return <line key={i} x1={x} y1={y} x2={x - 10} y2={y + 34} />;
			})}
		</g>
	) : null;

const Snow: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g fill="#ffffff" opacity={0.85}>
			{Array.from({length: 110}).map((_, i) => {
				const y = loop(rand(i, 4) * H + t * (40 + rand(i, 5) * 50), H + 40) - 20;
				const x = rand(i, 6) * W + Math.sin(t * 0.8 + i) * 18;
				return <circle key={i} cx={x} cy={y} r={2 + rand(i, 7) * 3} />;
			})}
		</g>
	) : null;

const DustMotes: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g fill="#fff4d6">
			{Array.from({length: 45}).map((_, i) => {
				const x = rand(i, 8) * W + Math.sin(t * 0.3 + i) * 30;
				const y = 200 + rand(i, 9) * 700 + Math.cos(t * 0.25 + i * 2) * 25;
				return <circle key={i} cx={x} cy={y} r={1.5 + rand(i, 10) * 2} opacity={0.25 + 0.35 * Math.abs(Math.sin(t * 0.9 + i))} />;
			})}
		</g>
	) : null;

const Fireflies: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g>
			{Array.from({length: 24}).map((_, i) => {
				const x = rand(i, 11) * W + Math.sin(t * 0.6 + i) * 60;
				const y = 450 + rand(i, 12) * 450 + Math.cos(t * 0.5 + i * 1.3) * 40;
				const glow = Math.max(0, Math.sin(t * 2 + i * 1.7));
				return (
					<g key={i} opacity={glow}>
						<circle cx={x} cy={y} r={14} fill="#fff1a0" opacity={0.25} filter="url(#blur8)" />
						<circle cx={x} cy={y} r={3.5} fill="#fff6c2" />
					</g>
				);
			})}
		</g>
	) : null;

const Embers: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g fill="#ffb35a">
			{Array.from({length: 30}).map((_, i) => {
				const y = H - loop(rand(i, 13) * H + t * (60 + rand(i, 14) * 60), H + 60);
				const x = rand(i, 15) * W + Math.sin(t * 1.5 + i) * 25;
				return <circle key={i} cx={x} cy={y} r={2 + rand(i, 16) * 2} opacity={0.4 + 0.5 * rand(i, 17)} />;
			})}
		</g>
	) : null;

const FirelightFlicker: React.FC<P> = ({t, layer}) => {
	if (layer !== 'front') return null;
	const flicker = 0.18 + 0.06 * Math.sin(t * 9.3) + 0.04 * Math.sin(t * 13.7 + 1);
	return <rect x={-200} y={-200} width={W + 400} height={H + 400} fill="url(#warmGlow)" opacity={flicker} style={{mixBlendMode: 'screen'}} />;
};

const FallingLeaves: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g>
			{Array.from({length: 16}).map((_, i) => {
				const y = loop(rand(i, 18) * H + t * (70 + rand(i, 19) * 40), H + 80) - 40;
				const x = rand(i, 20) * W + Math.sin(t * 1.2 + i) * 60;
				const r = (t * 90 + i * 40) % 360;
				return (
					<path key={i} d="M0,-9 C7,-5 7,5 0,9 C-7,5 -7,-5 0,-9 Z" fill={i % 2 ? '#c98a3c' : '#a8702c'}
						transform={`translate(${x} ${y}) rotate(${r})`} opacity={0.9} />
				);
			})}
		</g>
	) : null;

const SunRays: React.FC<P> = ({t, palette: p, layer}) =>
	layer === 'back' ? (
		<g opacity={0.16 + 0.04 * Math.sin(t * 0.5)} style={{mixBlendMode: 'screen'}}>
			{[-30, -12, 6, 24, 42].map((a, i) => (
				<path key={i} d="M0,0 L-70,1400 L70,1400 Z" fill={p.sun}
					transform={`translate(${p.sunX * W} ${p.sunY * H}) rotate(${a + Math.sin(t * 0.3 + i) * 2})`} />
			))}
		</g>
	) : null;

const Sparkles: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g fill="#fff8d0">
			{Array.from({length: 18}).map((_, i) => {
				const s = Math.max(0, Math.sin(t * 2.4 + i * 1.9));
				const x = 200 + rand(i, 21) * 1500;
				const y = 250 + rand(i, 22) * 600;
				return <path key={i} d="M0,-9 L2,-2 L9,0 L2,2 L0,9 L-2,2 L-9,0 L-2,-2 Z" transform={`translate(${x} ${y}) scale(${s})`} />;
			})}
		</g>
	) : null;

const Wind: React.FC<P> = ({t, layer}) =>
	layer === 'front' ? (
		<g fill="none" stroke="#ffffff" strokeWidth={3} strokeLinecap="round" opacity={0.3}>
			{Array.from({length: 7}).map((_, i) => {
				const x = loop(rand(i, 23) * W + t * 260, W + 600) - 300;
				const y = 250 + rand(i, 24) * 600;
				return <path key={i} d={`M${x},${y} q60,-18 120,0 t120,0`} />;
			})}
		</g>
	) : null;

export const ATMOSPHERE: Record<string, React.FC<P>> = {
	fog: Fog, mist: Mist, rain: Rain, snow: Snow, dust_motes: DustMotes, fireflies: Fireflies, embers: Embers,
	firelight_flicker: FirelightFlicker, falling_leaves: FallingLeaves, sun_rays: SunRays, sparkles: Sparkles, wind: Wind,
};
