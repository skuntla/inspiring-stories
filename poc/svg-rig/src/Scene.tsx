import React from 'react';
import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Captions} from './Captions';
import {Pip} from './Pip';
import {DURATION, FPS, eyeOpenness, isSpeaking, mouthAt} from './timing';

const INK = {stroke: '#3b2a20', strokeWidth: 3, strokeLinejoin: 'round' as const, strokeOpacity: 0.7};
const ease = (x: number) => (x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2);
// Camera as in the sandcastle film: [center x, center y, zoom], eased from -> to, clamped to the frame.
const CAMERA = {from: [960, 560, 1.0], to: [900, 640, 1.14]};

// Deterministic pseudo-random for scattering grass and flowers.
const rand = (i: number) => {
	const x = Math.sin(i * 12.9898) * 43758.5453;
	return x - Math.floor(x);
};

const Filters: React.FC = () => (
	<defs>
		{/* watercolor: wobbly edges plus a slight bleed */}
		<filter id="watercolor" x="-5%" y="-5%" width="110%" height="110%">
			<feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves={3} seed={7} result="noise" />
			<feDisplacementMap in="SourceGraphic" in2="noise" scale={14} xChannelSelector="R" yChannelSelector="G" result="wobble" />
			<feGaussianBlur in="wobble" stdDeviation={1.2} />
		</filter>
		<filter id="softEdge" x="-10%" y="-10%" width="120%" height="120%">
			<feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves={2} seed={3} result="noise" />
			<feDisplacementMap in="SourceGraphic" in2="noise" scale={3.5} xChannelSelector="R" yChannelSelector="G" />
		</filter>
		<filter id="fogBlur" x="-20%" y="-50%" width="140%" height="200%">
			<feGaussianBlur stdDeviation={38} />
		</filter>
		<filter id="farBlur">
			<feGaussianBlur stdDeviation={2.2} />
		</filter>
		<filter id="paper" x="0" y="0" width="100%" height="100%">
			<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={3} seed={11} />
			<feColorMatrix type="saturate" values="0" />
			<feComponentTransfer>
				<feFuncA type="linear" slope={0.9} />
			</feComponentTransfer>
		</filter>
		<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0" stopColor="#c9d3d2" />
			<stop offset="0.55" stopColor="#e8e0cc" />
			<stop offset="1" stopColor="#efe4c8" />
		</linearGradient>
		<radialGradient id="sun" cx="0.72" cy="0.22" r="0.35">
			<stop offset="0" stopColor="#fff6dc" stopOpacity={0.95} />
			<stop offset="1" stopColor="#fff6dc" stopOpacity={0} />
		</radialGradient>
		<radialGradient id="vignette" cx="0.5" cy="0.5" r="0.75">
			<stop offset="0.6" stopColor="#000" stopOpacity={0} />
			<stop offset="1" stopColor="#2a2418" stopOpacity={0.35} />
		</radialGradient>
	</defs>
);

const Grass: React.FC<{y: number; count: number; height: number; color: string; seed: number; sway: number}> = ({
	y, count, height, color, seed, sway,
}) => (
	<g>
		{Array.from({length: count}).map((_, i) => {
			const x = rand(seed + i) * 2200 - 140;
			const h = height * (0.6 + rand(seed + i + 99) * 0.7);
			const lean = (rand(seed + i + 7) - 0.5) * 30 + sway;
			return (
				<path
					key={i}
					d={`M${x},${y} Q${x + lean * 0.4},${y - h * 0.6} ${x + lean},${y - h} Q${x + lean * 0.3 + 6},${y - h * 0.55} ${x + 9},${y}`}
					fill={color}
				/>
			);
		})}
	</g>
);

export const Scene: React.FC = () => {
	const frame = useCurrentFrame();
	const t = frame / FPS;
	const e = ease(frame / DURATION);
	const zoom = CAMERA.from[2] + (CAMERA.to[2] - CAMERA.from[2]) * e;
	const hw = 960 / zoom, hh = 540 / zoom;
	const camX = Math.min(Math.max(CAMERA.from[0] + (CAMERA.to[0] - CAMERA.from[0]) * e, hw), 1920 - hw);
	const camY = Math.min(Math.max(CAMERA.from[1] + (CAMERA.to[1] - CAMERA.from[1]) * e, hh), 1080 - hh);
	// parallax: nearer layers drift further as the camera moves
	const pan = interpolate(frame, [0, DURATION], [0, -1]);
	const layer = (depth: number) => `translate(${(pan * 60 * depth).toFixed(2)} 0)`;
	const sway = Math.sin(t * 1.4) * 6;

	return (
		<AbsoluteFill style={{backgroundColor: '#e8e0cc'}}>
			<Audio src={staticFile('poc.wav')} />
			<svg viewBox="0 0 1920 1080" width={1920} height={1080}>
				<Filters />
				<g transform={`translate(960 540) scale(${zoom.toFixed(4)}) translate(${(-camX).toFixed(2)} ${(-camY).toFixed(2)})`}>
					{/* sky and sun glow */}
					<rect x={-100} y={-100} width={2120} height={1280} fill="url(#sky)" />
					<rect x={-100} y={-100} width={2120} height={1280} fill="url(#sun)" />

					{/* far hills, softened by distance */}
					<g transform={layer(0.15)} filter="url(#farBlur)">
						<path d="M-120,560 C200,470 420,500 640,540 C880,470 1120,450 1380,520 C1600,470 1820,480 2040,540 L2040,760 L-120,760 Z" fill="#a9b7a8" opacity={0.85} />
						{/* the great oak, faint in the distance */}
						<g opacity={0.55}>
							<rect x={1488} y={440} width={16} height={110} fill="#7d8a78" />
							<ellipse cx={1496} cy={420} rx={92} ry={62} fill="#8e9d8a" />
							<ellipse cx={1450} cy={446} rx={56} ry={40} fill="#8e9d8a" />
							<ellipse cx={1548} cy={444} rx={60} ry={42} fill="#8e9d8a" />
						</g>
					</g>

					{/* mid hills with the willow */}
					<g transform={layer(0.35)} filter="url(#watercolor)">
						<path d="M-120,640 C160,560 420,590 700,630 C980,570 1260,560 1520,610 C1720,580 1880,590 2040,620 L2040,820 L-120,820 Z" fill="#94a77d" {...INK} strokeOpacity={0.4} />
						<g transform="translate(330 470)">
							<path d="M4,190 C8,120 0,60 14,4 L28,4 C32,70 24,130 32,190 Z" fill="#6e5a44" {...INK} />
							<path d="M-110,40 C-120,-40 -20,-70 20,-66 C80,-70 150,-30 140,40 C90,20 -60,20 -110,40 Z" fill="#88a262" {...INK} />
							{Array.from({length: 17}).map((_, i) => {
								const x = -104 + i * 15;
								const len = 110 + Math.sin(i * 1.7) * 30 + (i > 3 && i < 13 ? 40 : 0);
								const s2 = Math.sin(t * 1.1 + i * 0.7) * 6;
								return (
									<path key={i} d={`M${x},${22 + Math.abs(i - 8) * 1.5} C${x - 6},${60} ${x - 10 + s2},${len * 0.7} ${x - 8 + s2 * 1.4},${len}`}
										fill="none" stroke={i % 2 ? '#7f9a5c' : '#93ae6c'} strokeWidth={7} strokeLinecap="round" />
								);
							})}
						</g>
					</g>

					{/* old wooden fence */}
					<g transform={layer(0.55)} filter="url(#softEdge)">
						{[0, 1, 2, 3, 4, 5, 6].map((i) => {
							const x = 1080 + i * 125;
							const tilt = (rand(i + 40) - 0.5) * 6;
							return <rect key={i} x={x} y={600 + i * 6} width={20} height={140} rx={4} fill="#8a7358" {...INK} transform={`rotate(${tilt} ${x + 10} ${740 + i * 6})`} />;
						})}
						<path d="M1070,640 L1860,672" stroke="#7a6349" strokeWidth={14} strokeLinecap="round" />
						<path d="M1070,690 L1860,718" stroke="#7a6349" strokeWidth={12} strokeLinecap="round" />
					</g>

					{/* meadow floor and the pale-earth path */}
					<g transform={layer(0.75)} filter="url(#watercolor)">
						<path d="M-120,720 C300,680 700,700 1000,720 C1360,690 1700,700 2040,720 L2040,1200 L-120,1200 Z" fill="#8ba06a" {...INK} strokeOpacity={0.45} />
						<path d="M1180,705 C1020,760 880,800 780,880 C700,950 640,1030 600,1200 L1080,1200 C1060,1060 1080,960 1150,880 C1210,810 1260,760 1300,710 Z" fill="#d8c7a0" {...INK} strokeOpacity={0.55} />
						<Grass y={760} count={70} height={60} color="#7d9360" seed={1} sway={sway * 0.5} />
						{Array.from({length: 26}).map((_, i) => (
							<circle key={i} cx={rand(i + 300) * 2000 - 40} cy={740 + rand(i + 400) * 120} r={6 + rand(i + 500) * 4} fill="#9b7bb8" opacity={0.85} />
						))}
					</g>

					{/* drifting fog bands */}
					<g filter="url(#fogBlur)" opacity={0.55}>
						<ellipse cx={400 + ((t * 18) % 2400) - 300} cy={700} rx={700} ry={90} fill="#f4f1ea" opacity={0.7} />
						<ellipse cx={1500 - ((t * 12) % 2400) + 300} cy={620} rx={800} ry={110} fill="#f4f1ea" opacity={0.6} />
						<ellipse cx={960 + Math.sin(t * 0.4) * 200} cy={820} rx={1100} ry={70} fill="#f4f1ea" opacity={0.45} />
					</g>

					{/* Pip on the path */}
					<g transform={`${layer(0.8)} translate(840 880) scale(1.0)`}>
						<Pip frame={frame} mouth={mouthAt('pip', t)} eye={eyeOpenness(frame)} speaking={isSpeaking('pip', t)} />
					</g>

					{/* a faint wisp in front of Pip's feet */}
					<g filter="url(#fogBlur)" opacity={0.35}>
						<ellipse cx={700 + Math.sin(t * 0.5) * 160} cy={960} rx={700} ry={40} fill="#f4f1ea" />
					</g>

					{/* foreground grass, nearest to the camera */}
					<g transform={layer(1.3)} filter="url(#softEdge)">
						<Grass y={1110} count={46} height={190} color="#6c8450" seed={70} sway={sway} />
						<Grass y={1120} count={30} height={120} color="#5e7646" seed={140} sway={sway * 1.3} />
					</g>
				</g>

				{/* paper grain and vignette stay fixed to the frame */}
				<rect width={1920} height={1080} filter="url(#paper)" opacity={0.07} style={{mixBlendMode: 'multiply'}} />
				<rect width={1920} height={1080} fill="url(#vignette)" />
			</svg>
			<Captions seconds={t} />
		</AbsoluteFill>
	);
};
