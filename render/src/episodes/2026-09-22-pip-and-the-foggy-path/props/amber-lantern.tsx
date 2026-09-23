import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A small old-fashioned brass lantern casting a gentle amber glow. Held by its ring, it hangs below the hand.
const Lantern: React.FC<DrawContext> = ({t}) => {
	const glow = 0.85 + 0.1 * Math.sin(t * 6) + 0.05 * Math.sin(t * 11);
	return (
		<g transform="translate(0 70)">
			<circle cx={0} cy={-40} r={130 * glow} fill="url(#warmGlow)" />
			<path d="M-10,-96 C-10,-112 10,-112 10,-96" fill="none" stroke="#9a7a2e" strokeWidth={4} />
			<path d="M-24,-82 L24,-82 L18,-96 L-18,-96 Z" fill="#b8932f" {...ink(2.5)} />
			<rect x={-22} y={-80} width={44} height={56} rx={6} fill="#ffcf6a" opacity={glow} {...ink(2.5)} />
			<path d="M-22,-62 L22,-62 M-22,-44 L22,-44 M0,-80 L0,-24" stroke="#9a7a2e" strokeWidth={2.5} />
			<path d="M-26,-24 L26,-24 L20,-10 L-20,-10 Z" fill="#b8932f" {...ink(2.5)} />
		</g>
	);
};

export const prop: Prop = {id: 'amber-lantern', width: 60, Component: Lantern};
