import React from 'react';
import {ink} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';
import {CrackedEarth, DryBush, Horizon, MudHouse, StoneWell, Villagers} from '../parts/village';

// The village the maps forgot: cracked fields, a few mud houses (some abandoned), a dead well, the
// dusty road running out at a stone marker, and women walking the long way to the river with pots.
const Background: React.FC<DrawContext> = ({t, palette: p}) => (
	<g>
		<Horizon t={t} />
		<MudHouse x={260} y={780} scale={0.9} lit={p.light < 0.5} />
		<MudHouse x={560} y={760} scale={0.7} broken />
		<MudHouse x={1480} y={770} scale={0.8} />
		<MudHouse x={1780} y={750} scale={0.6} broken />
		<CrackedEarth y={740} />
		{/* the road runs in from the front and stops at a stone marker */}
		<path d="M760,1300 C820,1080 900,900 960,760 L1010,760 C1060,900 1200,1080 1300,1300 Z" fill="#e6cfa4" opacity={0.8} />
		<path d="M978,760 L978,700 Q990,690 1002,700 L1002,760 Z" fill="#b7a98f" {...ink(2.5)} />
		<StoneWell x={1250} y={900} t={t} scale={0.6} water={false} dead />
		<DryBush x={120} y={960} seed={531} />
		<DryBush x={1700} y={990} scale={1.2} seed={533} />
		<Villagers t={t} palette={p} people={[
			{x0: 100, speed: 34, y: 742, scale: 0.28, who: 0},
			{x0: 420, speed: 34, y: 746, scale: 0.28, who: 1},
			{x0: 1200, speed: 30, y: 744, scale: 0.26, who: 2},
		]} />
		{/* drifting dust */}
		{[0, 1, 2, 3].map((i) => (
			<ellipse key={i} cx={((i * 600 + t * 40) % 2400) - 240} cy={900 + i * 40} rx={120} ry={10} fill="#f0dcb4" opacity={0.35} />
		))}
	</g>
);

export const location: Location = {id: 'dry-village', groundY: 900, backgroundGroundY: 800, propSlots: [[1560, 900], [360, 900]], Background};
