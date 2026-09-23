import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Defs, palette} from '../kit/style';
import type {Rig} from '../kit/types';
import {rig as kai} from '../series/quiet-lessons/characters/kai';
import {rig as ren} from '../series/quiet-lessons/characters/master-ren';

// Dev only: how characters' posture and gesture change with stance and mood. Edit ROWS to check a
// new character or gesture before it goes into an episode.
const ROWS: [Rig, [string, string][]][] = [
	[kai, [['stand', 'calm'], ['aim', 'calm'], ['aim', 'angry'], ['stand', 'sad'], ['sit', 'worried'], ['walk', 'calm'], ['stand', 'surprised']]],
	[ren, [['stand', 'calm'], ['aim', 'calm'], ['stand', 'happy'], ['stand', 'thoughtful'], ['sit', 'calm'], ['walk', 'calm'], ['stand', 'neutral']]],
];

export const ActingSheet: React.FC = () => {
	const pal = palette('morning');
	return (
		<AbsoluteFill style={{backgroundColor: '#efe7d4'}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%">
				<Defs palette={pal} />
				{ROWS.map(([rig, poses], r) =>
					poses.map(([stance, mood], i) => {
						const x = 150 + i * 265;
						const y = 470 + r * 500;
						return (
							<g key={`${r}-${i}`}>
								{stance === 'sit' && <rect x={x - 70} y={y - 122} width={170} height={20} rx={6} fill="#9a6a42" />}
								<g transform={`translate(${x} ${y}) scale(0.85)`}>
									<rig.Component t={1.3} palette={pal} timeOfDay="morning" stance={stance} mood={mood} mouth="rest" eye={1}
										speaking={false} facing="right" walkSpeed={stance === 'walk' ? 100 : 0} />
								</g>
								<text x={x} y={y + 40} fontSize={24} fontFamily="system-ui" textAnchor="middle" fill="#3b2a20">{stance} / {mood}</text>
							</g>
						);
					}),
				)}
			</svg>
		</AbsoluteFill>
	);
};
