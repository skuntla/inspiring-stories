import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// Three round golden buns with dark red berry filling.
const Bun: React.FC<{x: number; y: number; s: number}> = ({x, y, s}) => (
	<g transform={`translate(${x} ${y}) scale(${s})`}>
		<path d="M-26,0 C-28,-30 28,-30 26,0 Z" fill="#e0a857" {...ink(2.5)} />
		<path d="M-12,-14 C-6,-22 6,-22 12,-14 C6,-10 -6,-10 -12,-14 Z" fill="#8e2331" />
		<path d="M-18,-20 C-12,-26 -4,-27 2,-26" fill="none" stroke="#f3cf8e" strokeWidth={3} strokeLinecap="round" />
	</g>
);

const Buns: React.FC<DrawContext> = () => (
	<g filter="url(#softEdge)">
		<Bun x={-30} y={0} s={1} />
		<Bun x={28} y={0} s={0.95} />
		<Bun x={0} y={-18} s={0.9} />
	</g>
);

export const prop: Prop = {id: 'berry-buns', width: 110, Component: Buns};
