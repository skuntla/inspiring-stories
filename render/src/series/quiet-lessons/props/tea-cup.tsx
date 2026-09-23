import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A small white cup of chai on a saucer, with a curl of steam.
const Cup: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)">
		{[0, 1].map((i) => (
			<path key={i} d={`M${-8 + i * 14},-52 c${-10 + Math.sin(t * 1.5 + i) * 6},-16 ${14},-26 ${2},-46`} fill="none"
				stroke="#ffffff" strokeWidth={4} strokeLinecap="round" opacity={0.45 + 0.2 * Math.sin(t * 2 + i)} />
		))}
		<ellipse cx={0} cy={-4} rx={44} ry={8} fill="#f3eee2" {...ink(2.5)} />
		<path d="M-28,-48 L-22,-10 C-18,-4 18,-4 22,-10 L28,-48 Z" fill="#fbf7ee" {...ink(2.5)} />
		<ellipse cx={0} cy={-48} rx={28} ry={6} fill="#c08a52" {...ink(2)} />
		<path d="M28,-40 C44,-40 44,-20 26,-20" fill="none" stroke="#3b2a20" strokeWidth={6} />
		<path d="M28,-40 C44,-40 44,-20 26,-20" fill="none" stroke="#fbf7ee" strokeWidth={3} />
	</g>
);

export const prop: Prop = {id: 'tea-cup', width: 90, Component: Cup};
