import React from 'react';
import {ink} from '../../kit/style';
import {lastWordAt} from '../../kit/spoken';
import type {DrawContext, Location} from '../../kit/types';

// Close on a brass compass on a wooden desk in warm light. The needle swings, slows, and settles on
// north exactly as the shot's last word starts ("...like a compass finding north").
export const about = "Close-up of a brass compass; the needle swings and settles on north on the shot's last spoken word.";

/** Needle angle (degrees) at time t for a needle that settles at `settle` seconds. */
export const swing = (t: number, settle: number) => {
	if (t >= settle) return 0;
	const decay = 1 - Math.pow(t / settle, 1.6);
	return 70 * decay * Math.sin((2 * Math.PI * t) / 1.5 + 0.6);
};

const Background: React.FC<DrawContext> = ({t, words}) => {
	const settle = lastWordAt(words, 3);
	const glow = t >= settle ? Math.min(1, (t - settle) / 0.8) : 0;
	return (
		<g>
			<rect x={-200} y={-200} width={2320} height={1480} fill="#9a6a42" />
			{Array.from({length: 8}).map((_, i) => (
				<path key={i} d={`M-200,${80 + i * 140} C400,${60 + i * 140} 1400,${110 + i * 140} 2120,${80 + i * 140}`} fill="none" stroke="#8a5c38" strokeWidth={5} />
			))}
			<path d="M1100,-200 L2120,-200 L2120,1280 L400,1280 Z" fill="#fff1c4" opacity={0.18} style={{mixBlendMode: 'screen'}} />
			<ellipse cx={980} cy={600} rx={380} ry={60} fill="#3e2918" opacity={0.35} />
			<g transform="translate(960 520)">
				<circle cx={0} cy={0} r={360} fill="url(#warmGlow)" opacity={0.4 + 0.5 * glow} />
				<circle cx={0} cy={-330} r={40} fill="none" stroke="#b8932f" strokeWidth={16} />
				<circle cx={0} cy={0} r={300} fill="#c9a13b" {...ink(5)} />
				<circle cx={0} cy={0} r={250} fill="#f6efdc" {...ink(3)} />
				{Array.from({length: 36}).map((_, i) => (
					<path key={i} d={`M0,-240 L0,${i % 9 === 0 ? -205 : -225}`} stroke="#3b2a20" strokeWidth={i % 9 === 0 ? 5 : 2} transform={`rotate(${i * 10})`} />
				))}
				{['N', 'E', 'S', 'W'].map((d, i) => (
					<text key={d} x={0} y={-160} textAnchor="middle" fontSize={56} fontFamily="Georgia, serif" fill={d === 'N' ? '#c8323a' : '#3b2a20'}
						transform={`rotate(${i * 90}) rotate(${-i * 90} 0 -178)`}>{d}</text>
				))}
				<g transform={`rotate(${swing(t, settle)})`}>
					<path d="M0,-200 L24,0 L-24,0 Z" fill="#c8323a" {...ink(3)} />
					<path d="M0,200 L24,0 L-24,0 Z" fill="#3b3a3a" {...ink(3)} />
				</g>
				<circle cx={0} cy={0} r={22} fill="#b8932f" {...ink(3)} />
			</g>
		</g>
	);
};

export const location: Location = {id: 'compass-closeup', interior: true, groundY: 880, propSlots: [], Background};
