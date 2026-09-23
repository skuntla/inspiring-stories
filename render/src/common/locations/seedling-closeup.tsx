import React from 'react';
import {ink} from '../../kit/style';
import type {DrawContext, Location} from '../../kit/types';

export const about = "Close-up of one seedling in damp soil; its stem rises and two leaves unfurl.";

// Close on one seedling in damp soil at dusk: its stem rises and two leaves unfurl, the "next seed".
const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const grow = Math.min(1, t / 3.2);
	const open = Math.max(0, Math.min(1, (t - 1.2) / 2.4));
	const stem = 60 + 300 * grow;
	const sway = Math.sin(t * 1.2) * 3;
	return (
		<g>
			<rect x={-200} y={-200} width={2320} height={1480} fill={p.skyMid} />
			<circle cx={p.sunX * 1920} cy={p.sunY * 1080} r={520} fill="url(#sunGlow)" />
			<ellipse cx={960} cy={1120} rx={1300} ry={380} fill="#5a3c26" {...ink(4)} />
			<ellipse cx={960} cy={880} rx={340} ry={40} fill="#3e2918" opacity={0.5} />
			<g transform={`translate(960 880) rotate(${sway})`}>
				<path d={`M0,0 C-10,${-stem * 0.4} 12,${-stem * 0.7} 0,${-stem}`} fill="none" stroke="#3b2a20" strokeWidth={18} strokeLinecap="round" />
				<path d={`M0,0 C-10,${-stem * 0.4} 12,${-stem * 0.7} 0,${-stem}`} fill="none" stroke="#5f9a44" strokeWidth={12} strokeLinecap="round" />
				<g transform={`translate(0 ${-stem})`}>
					<g transform={`rotate(${-70 + 55 * open})`}>
						<path d="M0,0 C-30,-20 -120,-30 -160,0 C-120,30 -30,20 0,0 Z" fill="#7cba5a" {...ink(3)} />
						<path d="M-10,0 L-140,0" stroke="#5f9a44" strokeWidth={3} />
					</g>
					<g transform={`rotate(${70 - 55 * open})`}>
						<path d="M0,0 C30,-20 120,-30 160,0 C120,30 30,20 0,0 Z" fill="#8fce68" {...ink(3)} />
						<path d="M10,0 L140,0" stroke="#5f9a44" strokeWidth={3} />
					</g>
				</g>
			</g>
		</g>
	);
};

export const location: Location = {id: 'seedling-closeup', interior: true, groundY: 880, propSlots: [], Background};
