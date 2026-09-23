import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// An old green metal watering can with a long spout. Drawn hanging from its handle (the origin),
// spout forward, with a thin stream of water; works held in a hand or set on the ground.
const Can: React.FC<DrawContext> = ({t}) => (
	<g filter="url(#softEdge)" transform="translate(-10 20) rotate(14)">
		<path d="M-40,0 C-40,-34 40,-34 40,0" fill="none" stroke="#3b2a20" strokeWidth={9} strokeLinecap="round" />
		<path d="M-40,0 C-40,-34 40,-34 40,0" fill="none" stroke="#4f7a3a" strokeWidth={5} strokeLinecap="round" />
		<path d="M-50,0 L50,0 L44,80 L-44,80 Z" fill="#5f8a44" {...ink(3)} />
		<path d="M40,30 L120,-10 L126,-2 L48,48 Z" fill="#5f8a44" {...ink(2.5)} />
		<ellipse cx={126} cy={-8} rx={8} ry={12} fill="#4f7a3a" {...ink(2)} transform="rotate(-30 126 -8)" />
		{Array.from({length: 6}).map((_, i) => {
			const d = ((t * 60 + i * 30) % 180);
			return <circle key={i} cx={132 + d * 0.25} cy={4 + d} r={3} fill="#9fd0f0" opacity={1 - d / 180} />;
		})}
	</g>
);

export const prop: Prop = {id: 'watering-can', width: 120, Component: Can};
