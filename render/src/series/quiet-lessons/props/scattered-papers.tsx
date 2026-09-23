import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// Loose sheets of paper and yellow sticky notes spread messily across the desk.
// the papers stir a little, as if in a draught
const Papers: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)" transform={`rotate(${Math.sin(t * 1.7) * 0.8})`}>
		<path d="M-120,0 L-40,-16 L40,-6 L-44,6 Z" fill="#fbf7ee" {...ink(2.5)} />
		<path d="M-60,-2 L30,-22 L110,-10 L20,4 Z" fill="#f3eee2" {...ink(2.5)} />
		<path d="M-20,-30 L50,-56 L66,-10 L-4,12 Z" fill="#fbf7ee" {...ink(2.5)} transform="rotate(-8)" />
		<path d="M-4,-24 L40,-40 M4,-12 L46,-26" stroke="#9aa3ad" strokeWidth={2} transform="rotate(-8)" />
		<rect x={70} y={-30} width={34} height={30} fill="#f6d65a" {...ink(2)} transform={`rotate(${12 + Math.sin(t * 2.3) * 6} 86 -15)`} />
		<rect x={-100} y={-36} width={30} height={28} fill="#f6d65a" {...ink(2)} transform="rotate(-14 -85 -22)" />
		<rect x={-40} y={-44} width={28} height={26} fill="#f7a8b8" {...ink(2)} transform="rotate(8 -26 -31)" />
	</g>
);

export const prop: Prop = {id: 'scattered-papers', width: 240, Component: Papers};
