import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';
import {CrackedEarth, DryBush, Horizon, MudHouse, Neem} from '../parts/village';

// Velu's stony plot at the end of the road: the pit he digs (a brick-lined hole just in front of where
// a character at center_left strikes), the neem tree that stays green, his small hut, and a clay lamp
// that burns at night.
export const PIT_X = 900;

const Background: React.FC<DrawContext> = ({t, palette: p}) => {
	const night = p.light < 0.5;
	return (
		<g>
			<Horizon t={t} />
			<MudHouse x={230} y={790} scale={0.95} lit={night} />
			<CrackedEarth y={760} seed={541} />
			<Neem x={1560} y={880} scale={1.35} t={t} />
			<DryBush x={1880} y={960} seed={543} />
			{/* the pit */}
			<ellipse cx={PIT_X} cy={906} rx={140} ry={36} fill="#3e2f22" {...ink(3.5)} />
			<path d={`M${PIT_X - 140},906 A140,36 0 0 0 ${PIT_X + 140},906`} fill="none" stroke="#a0522d" strokeWidth={10} opacity={0.8} />
			<ellipse cx={PIT_X} cy={914} rx={110} ry={24} fill="#241a12" />
			{/* the clay lamp */}
			<g transform={`translate(${PIT_X + 190} 910)`}>
				{night && <circle cx={0} cy={-30} r={170} fill="url(#warmGlow)" opacity={0.85 + 0.1 * Math.sin(t * 11)} />}
				<path d="M-22,0 Q0,14 22,0 L16,-12 L-16,-12 Z" fill="#b5602f" {...ink(2)} />
				{night && <path d={`M0,-12 C-6,-24 -2,-34 ${Math.sin(t * 13) * 2},-42 C4,-34 6,-24 0,-12 Z`} fill="#ffd98a" />}
			</g>
		</g>
	);
};

export const location: Location = {
	id: 'velu-plot', groundY: 900, backgroundGroundY: 800,
	propSlots: [[1210, 900], [470, 900], [1330, 900]],
	Background,
};
