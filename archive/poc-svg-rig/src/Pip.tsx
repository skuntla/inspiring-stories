import React from 'react';
import type {Shape} from './timing';

// Pip, three-quarter view facing right. Local origin: between the feet, on the ground.
const FUR = '#8a5a3b';
const FUR_DARK = '#6b4129';
const FUR_TIP = '#c99a68';
const CREAM = '#f1e1c4';
const CREAM_SHADE = '#dcc49f';
const NOSE = '#c26b76';
const SCARF = '#6f8f4e';
const SCARF_DARK = '#56733b';
const INK = '#3b2a20';
const OUTLINE = {stroke: INK, strokeWidth: 3.5, strokeLinejoin: 'round' as const};

/** Spiky back: points alternate between an inner and an outer ellipse along an arc. */
const spines = (cx: number, cy: number, rx: number, ry: number, spike: number, from: number, to: number, n: number) => {
	const pts: string[] = [];
	for (let i = 0; i <= n * 2; i++) {
		const a = ((from + ((to - from) * i) / (n * 2)) * Math.PI) / 180;
		const out = i % 2 === 1 ? spike : 0;
		pts.push(`${(cx + Math.cos(a) * (rx + out)).toFixed(1)},${(cy - Math.sin(a) * (ry + out)).toFixed(1)}`);
	}
	return pts;
};

const Mouth: React.FC<{shape: Shape}> = ({shape}) => {
	// Drawn around (0,0) = mouth center, just under the snout.
	const lip = {fill: 'none', stroke: INK, strokeWidth: 3.2, strokeLinecap: 'round' as const};
	const inside = '#5a2630';
	switch (shape) {
		case 'closed':
			return <path d="M-13,0 Q0,2 13,0" {...lip} strokeWidth={4} />;
		case 'fv':
			return (
				<g>
					<path d="M-12,-2 Q0,9 12,-2 Z" fill={inside} stroke={INK} strokeWidth={2.4} />
					<rect x={-7} y={-3} width={14} height={4} rx={1.5} fill="#fbf6ec" />
				</g>
			);
		case 'consonant':
			return (
				<g>
					<path d="M-13,-2 Q0,11 13,-2 Q0,2 -13,-2 Z" fill={inside} stroke={INK} strokeWidth={2.4} />
					<path d="M-8,-1 L8,-1" stroke="#fbf6ec" strokeWidth={3} strokeLinecap="round" />
				</g>
			);
		case 'ee':
			return (
				<g>
					<path d="M-16,-3 Q0,11 16,-3 Q0,0 -16,-3 Z" fill={inside} stroke={INK} strokeWidth={2.4} />
					<path d="M-10,-1.5 L10,-1.5" stroke="#fbf6ec" strokeWidth={2.5} strokeLinecap="round" />
				</g>
			);
		case 'mid':
			return (
				<g>
					<path d="M-13,-3 Q0,16 13,-3 Q0,-1 -13,-3 Z" fill={inside} stroke={INK} strokeWidth={2.4} />
					<ellipse cx={0} cy={6} rx={6} ry={3} fill="#c9606f" />
				</g>
			);
		case 'open':
			return (
				<g>
					<path d="M-12,-4 Q0,24 12,-4 Q0,-2 -12,-4 Z" fill={inside} stroke={INK} strokeWidth={2.4} />
					<ellipse cx={0} cy={11} rx={7} ry={4} fill="#c9606f" />
				</g>
			);
		case 'round':
			return <ellipse cx={0} cy={3} rx={6.5} ry={8} fill={inside} stroke={INK} strokeWidth={2.4} />;
		default:
			return <path d="M-12,-1 Q0,6 12,-1" {...lip} />;
	}
};

export const Pip: React.FC<{
	frame: number;
	mouth: Shape;
	eye: number; // 1 open, 0 closed
	speaking: boolean;
}> = ({frame, mouth, eye, speaking}) => {
	const t = frame / 30;
	const breathe = 1 + Math.sin(t * 2.2) * 0.012;
	const headTilt = Math.sin(t * 1.3) * 1.2 + (speaking ? Math.sin(t * 7.5) * 1.6 : 0);
	const scarfSway = Math.sin(t * 1.7) * 6;
	const tuftSway = Math.sin(t * 2.4 + 1) * 5;
	const back = spines(-10, -118, 138, 108, 26, 205, 62, 17);

	return (
		<g filter="url(#softEdge)">
			{/* ground shadow */}
			<ellipse cx={20} cy={4} rx={150} ry={16} fill="#3d4a2c" opacity={0.28} />
			{/* feet */}
			<ellipse cx={-50} cy={-4} rx={30} ry={13} fill={FUR_DARK} {...OUTLINE} />
			<ellipse cx={62} cy={-4} rx={30} ry={13} fill={FUR_DARK} {...OUTLINE} />

			<g transform={`translate(0 ${(-(breathe - 1) * 120).toFixed(2)}) scale(1 ${breathe.toFixed(4)})`}>
				{/* belly and back spines */}
				<ellipse cx={30} cy={-80} rx={112} ry={78} fill={CREAM_SHADE} />
				<path
					d={`M${back[0]} L${back.slice(1).join(' L')} C130,-190 158,-70 112,-30 C66,4 -60,6 -118,-26 C-150,-44 -152,-60 ${back[0]} Z`}
					fill={FUR}
					{...OUTLINE}
				/>
				{/* lighter spine tips */}
				{back.filter((_, i) => i % 2 === 1).map((p, i) => {
					const [x, y] = p.split(',').map(Number);
					return <line key={i} x1={x * 0.93 + -10 * 0.07} y1={y * 0.93 + -118 * 0.07} x2={x} y2={y} stroke={FUR_TIP} strokeWidth={5} strokeLinecap="round" />;
				})}
				<ellipse cx={-30} cy={-120} rx={70} ry={48} fill={FUR_DARK} opacity={0.18} />
				{/* paws */}
				<ellipse cx={128} cy={-44} rx={17} ry={12} fill={CREAM} {...OUTLINE} strokeWidth={2.5} />
				<ellipse cx={92} cy={-36} rx={16} ry={11} fill={CREAM} {...OUTLINE} strokeWidth={2.5} />

				{/* head */}
				<g transform={`rotate(${headTilt.toFixed(2)} 105 -110)`}>
					{/* the one spine that always sticks up */}
					<path
						d={`M52,-176 C48,-206 ${56 + tuftSway},-236 ${70 + tuftSway},-246 C${64 + tuftSway},-228 66,-204 74,-178 Z`}
						fill={FUR}
						{...OUTLINE}
					/>
					<ellipse cx={62} cy={-168} rx={17} ry={15} fill={FUR} {...OUTLINE} strokeWidth={3} />
					<ellipse cx={63} cy={-167} rx={8} ry={7} fill={CREAM_SHADE} />
					{/* face and snout */}
					<path
						d="M40,-150 C60,-190 130,-190 160,-150 C180,-128 205,-118 222,-104 C230,-96 226,-84 214,-80 C190,-72 170,-64 140,-62 C95,-60 50,-80 40,-110 Z"
						fill={CREAM}
						{...OUTLINE}
					/>
					<circle cx={225} cy={-98} r={11} fill={NOSE} {...OUTLINE} strokeWidth={2.5} />
					<circle cx={222} cy={-102} r={3.5} fill="#f4c9cf" />
					<ellipse cx={138} cy={-92} rx={15} ry={9} fill="#e9a1a6" opacity={0.45} />
					{/* eye with blink */}
					<g>
						<ellipse cx={128} cy={-130} rx={16} ry={19} fill="#1d1512" />
						<circle cx={133} cy={-137} r={6} fill="#ffffff" />
						<circle cx={123} cy={-123} r={2.5} fill="#ffffff" opacity={0.8} />
						<rect
							x={108}
							y={-152}
							width={40}
							height={42 * (1 - eye)}
							fill={CREAM}
							stroke={eye < 0.95 ? INK : 'none'}
							strokeWidth={2}
						/>
						<path d="M112,-152 Q128,-160 146,-150" fill="none" stroke={FUR_DARK} strokeWidth={3} strokeLinecap="round" />
					</g>
					<g transform="translate(186 -84) scale(1.55)">
						<Mouth shape={mouth} />
					</g>
				</g>

				{/* moss-green knitted scarf */}
				<path d="M44,-92 C80,-70 130,-62 168,-72 L172,-48 C130,-38 78,-44 38,-66 Z" fill={SCARF} {...OUTLINE} />
				{[0, 1, 2, 3, 4, 5, 6].map((i) => (
					<line key={i} x1={52 + i * 18} y1={-84 + i * 2.6} x2={50 + i * 18} y2={-62 + i * 1.6} stroke={SCARF_DARK} strokeWidth={2} opacity={0.6} />
				))}
				<g transform={`rotate(${scarfSway.toFixed(2)} 60 -62)`}>
					<path d="M52,-66 C44,-30 40,0 46,26 L72,22 C66,-2 70,-32 76,-60 Z" fill={SCARF} {...OUTLINE} />
					<path d="M46,26 l4,10 M56,25 l2,11 M66,23 l3,10" stroke={SCARF_DARK} strokeWidth={3} strokeLinecap="round" />
				</g>
			</g>
		</g>
	);
};
