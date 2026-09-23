import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Prop} from '../../../kit/types';

// A smartphone lying face up, its screen lit with stacked notification badges that keep blinking.
const Phone: React.FC<DrawContext> = ({t}) => {
	const blink = 0.55 + 0.45 * Math.max(0, Math.sin(t * 5));
	return (
		<g filter="url(#softEdge)">
			<ellipse cx={0} cy={-40} rx={70} ry={50} fill="#bfe3ff" opacity={0.25 * blink} filter="url(#blur8)" />
			<path d="M-46,0 L-30,-62 L34,-62 L48,0 Z" fill="#2c2f36" {...ink(3)} />
			<path d="M-38,-6 L-25,-56 L28,-56 L40,-6 Z" fill="#9fd0f0" opacity={0.6 + 0.4 * blink} />
			{[0, 1, 2].map((i) => (
				<rect key={i} x={-22 + i * 2} y={-48 + i * 14} width={42} height={9} rx={3} fill="#ffffff" opacity={0.85} />
			))}
			<circle cx={34} cy={-60} r={10} fill="#e0463c" opacity={blink} {...ink(2)} />
			{/* notification cards keep popping up out of the phone */}
			{[0, 1, 2].map((i) => {
				const k = ((t * 0.55 + i / 3) % 1);
				return (
					<g key={`n${i}`} opacity={Math.min(1, k * 5) * (1 - k)} transform={`translate(${(i - 1) * 46} ${-80 - k * 170}) scale(${0.7 + k * 0.4})`}>
						<rect x={-38} y={-18} width={76} height={30} rx={10} fill="#ffffff" {...ink(2)} />
						<circle cx={-24} cy={-3} r={6} fill={['#e0463c', '#3f7f86', '#d9b25c'][i]} />
						<path d="M-12,-8 L26,-8 M-12,2 L16,2" stroke="#9aa3ad" strokeWidth={3} strokeLinecap="round" />
					</g>
				);
			})}
		</g>
	);
};

export const prop: Prop = {id: 'blinking-phone', width: 100, Component: Phone};
