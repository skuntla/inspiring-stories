import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';
import {Coin} from '../../../vendor/fluent-emoji/Coin';

// Close on Velu's open, work-worn palm holding two copper coins (one too many), the counter below.
const COPPER = {'#F9C23C': '#d9894a', '#D3883E': '#a55a2c'};

const Background: React.FC<DrawContext> = ({t}) => {
	const bob = Math.sin(t * 1.2) * 4;
	return (
		<g>
			<rect x={-240} y={-240} width={2400} height={1560} fill="#9a6a42" />
			{Array.from({length: 7}).map((_, i) => (
				<path key={i} d={`M-240,${60 + i * 170} C400,${40 + i * 170} 1400,${90 + i * 170} 2160,${60 + i * 170}`} fill="none" stroke="#8a5c38" strokeWidth={6} />
			))}
			<g transform={`translate(960 ${470 + bob}) scale(1.55)`}>
				{/* wrist and palm, seen from above: a lighter palm, four fingers and a thumb */}
				<path d="M-110,440 C-120,330 -150,200 -140,90 C-130,10 140,10 160,90 C176,200 140,330 120,440 Z" fill="#8d5a3b" {...ink(5)} />
				{[[-120, 60], [-50, 40], [20, 40], [90, 56]].map(([x, top], i) => (
					<g key={i}>
						<path d={`M${x},${top + 40} C${x - 4},${top - 120 + i * 8} ${x + 64},${top - 120 + i * 8} ${x + 60},${top + 40} Z`} fill="#8d5a3b" {...ink(5)} />
						<path d={`M${x + 12},${top - 30} q18,8 36,0`} fill="none" stroke="#6e4430" strokeWidth={4} strokeLinecap="round" />
					</g>
				))}
				<path d="M-140,150 C-250,110 -300,20 -260,-10 C-220,-20 -180,50 -130,100 Z" fill="#8d5a3b" {...ink(5)} />
				<ellipse cx={10} cy={170} rx={130} ry={120} fill="#c08a64" />
				<path d="M-90,110 Q10,160 120,100 M-70,220 Q20,250 110,200 M-40,130 Q-20,220 20,300" fill="none" stroke="#9a6a4a" strokeWidth={5} strokeLinecap="round" />
				<g transform="translate(-40 110)"><Coin size={150} recolor={COPPER} /></g>
				<g transform="translate(70 160) rotate(12)"><Coin size={150} recolor={COPPER} /></g>
			</g>
		</g>
	);
};

export const location: Location = {id: 'coins-in-palm', interior: true, groundY: 1040, propSlots: [], Background};
