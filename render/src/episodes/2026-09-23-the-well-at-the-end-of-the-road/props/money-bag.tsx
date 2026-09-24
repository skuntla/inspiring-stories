import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A heavy maroon velvet pouch tied with gold cord, gold coins spilling from its mouth.
const Bag: React.FC<DrawContext> = ({t}) => (
	<g>
		<path d="M-60,-4 C-80,-60 -50,-110 -18,-118 L18,-118 C50,-110 80,-60 60,-4 Q0,8 -60,-4 Z" fill="#7a2e2a" {...ink(3)} />
		<path d="M-22,-118 C-30,-140 -10,-150 0,-136 C10,-150 30,-140 22,-118 Z" fill="#8e3a33" {...ink(2.5)} />
		<path d="M-24,-116 Q0,-106 24,-116" fill="none" stroke="#e9c046" strokeWidth={6} />
		{[[-74, -4], [-50, -10], [68, -6], [90, -2]].map(([x, y], i) => (
			<ellipse key={i} cx={x} cy={y} rx={16} ry={6} fill="#e9c046" {...ink(1.5)} />
		))}
		<circle cx={-20} cy={-70} r={4} fill="#fff6c8" opacity={0.6 + 0.4 * Math.sin(t * 4)} />
	</g>
);
export const prop: Prop = {id: 'money-bag', width: 180, Component: Bag};
