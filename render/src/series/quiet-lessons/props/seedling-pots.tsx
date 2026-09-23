import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A row of three terracotta pots with tiny green seedlings that sway a little.
const Pots: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)">
		{[-70, 0, 70].map((x, i) => (
			<g key={i} transform={`translate(${x} 0)`}>
				<g transform={`rotate(${Math.sin(t * 1.3 + i) * 4} 0 -46)`}>
					<path d="M0,-46 L0,-78" stroke="#4f7a3a" strokeWidth={4} />
					<path d="M0,-72 C-18,-80 -22,-94 -4,-92 C0,-86 0,-78 0,-72 Z" fill="#7cba5a" {...ink(1.8)} />
					<path d="M0,-66 C18,-74 22,-88 4,-86 C0,-80 0,-72 0,-66 Z" fill="#7cba5a" {...ink(1.8)} />
				</g>
				<path d="M-30,-48 L30,-48 L22,0 L-22,0 Z" fill="#c0643a" {...ink(2.5)} />
				<rect x={-34} y={-54} width={68} height={10} rx={3} fill="#b0582f" {...ink(2)} />
			</g>
		))}
	</g>
);

export const prop: Prop = {id: 'seedling-pots', width: 220, Component: Pots};
