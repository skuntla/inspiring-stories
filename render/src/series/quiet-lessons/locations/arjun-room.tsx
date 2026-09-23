import React from 'react';
import {ink, rand} from '../../../kit/style';
import type {DrawContext, Location} from '../../../kit/types';

// Arjun's small study: a wooden desk under a window, a desk lamp, a chair and a narrow bookshelf
// against warm terracotta walls. The lamp glows more as the light falls.
const Background: React.FC<DrawContext> = ({t, palette: p, timeOfDay}) => {
	// the lamp matters more as the light falls, and flickers a little at night
	const flicker = timeOfDay === 'night' ? 0.06 * Math.sin(t * 7.3) + 0.04 * Math.sin(t * 13.1) : 0;
	const lamp = Math.max(0, 1 - p.light) * 1.1 + 0.15 + 0.03 * Math.sin(t * 2) + flicker;
	// morning sun creeps in from the window over the first seconds of a morning shot
	const sunIn = timeOfDay === 'morning' ? Math.min(1, t / 5) : 0;
	const sec = t % 60;
	return (
		<g>
			<g filter="url(#watercolor)">
				<rect x={-200} y={-200} width={2320} height={1100} fill="#dca07a" />
				<rect x={-200} y={640} width={2320} height={22} fill="#c98a64" />
				<rect x={-200} y={800} width={2320} height={500} fill="#9a4a3a" {...ink(3, 0.5)} />
				{Array.from({length: 12}).map((_, i) => (
					<path key={i} d={`M${-200 + i * 200},800 L${-320 + i * 230},1300`} stroke="#86402f" strokeWidth={3} />
				))}
				{/* a striped cotton dhurrie rug */}
				<path d="M560,900 L1420,900 L1520,1010 L460,1010 Z" fill="#d9b25c" {...ink(2.5, 0.7)} />
				{[0.22, 0.45, 0.68].map((f, i) => (
					<path key={i} d={`M${560 - 100 * f},${900 + 110 * f} L${1420 + 100 * f},${900 + 110 * f}`} stroke="#3f7f86" strokeWidth={10} />
				))}
			</g>
			{/* window above the desk: follows the time of day */}
			<g>
				<rect x={1170} y={180} width={400} height={330} rx={10} fill="#7a5236" {...ink(3.5)} />
				<rect x={1190} y={200} width={360} height={290} fill={p.skyMid} />
				<rect x={1190} y={200} width={360} height={150} fill={p.skyTop} opacity={0.6} />
				<circle cx={1480} cy={260} r={26} fill={p.sun} opacity={0.9} />
				<path d="M1370,200 L1370,490 M1190,345 L1550,345" stroke="#7a5236" strokeWidth={10} />
			</g>
			{/* wall clock: the second hand ticks, the minute hand creeps */}
			<g transform="translate(760 300)">
				<circle cx={0} cy={0} r={62} fill="#f6efdc" {...ink(3.5)} />
				{Array.from({length: 12}).map((_, i) => (
					<path key={i} d="M0,-52 L0,-44" stroke="#3b2a20" strokeWidth={3} transform={`rotate(${i * 30})`} />
				))}
				<path d="M0,0 L0,-30" stroke="#3b2a20" strokeWidth={6} strokeLinecap="round" transform={`rotate(${300 + t * 0.5})`} />
				<path d="M0,0 L0,-44" stroke="#3b2a20" strokeWidth={4} strokeLinecap="round" transform={`rotate(${60 + t * 6})`} />
				<path d="M0,6 L0,-48" stroke="#c8323a" strokeWidth={2} transform={`rotate(${Math.floor(sec) * 6})`} />
				<circle cx={0} cy={0} r={5} fill="#3b2a20" />
			</g>
			{/* narrow bookshelf */}
			<g>
				<rect x={140} y={300} width={260} height={500} fill="#7a5236" {...ink(3.5)} />
				{[380, 480, 580, 680].map((y, r) => (
					<g key={r}>
						<rect x={156} y={y} width={228} height={10} fill="#5f3e28" />
						{Array.from({length: 8}).map((_, i) => (
							<rect key={i} x={162 + i * 27} y={y - 62 + rand(i, r + 3) * 14} width={22} height={62 - rand(i, r + 3) * 14}
								fill={['#3f7f86', '#b8653a', '#d9b25c', '#6d8b4a'][(i + r) % 4]} {...ink(1.5, 0.7)} />
						))}
					</g>
				))}
			</g>
			{/* morning light spreading from the window across the wall and floor */}
			{sunIn > 0 && (
				<path d={`M1190,200 L1550,200 L${1560 + 260 * sunIn},1000 L${1100 - 420 * sunIn},1000 Z`} fill="#fff1c4"
					opacity={0.28 * sunIn} style={{mixBlendMode: 'screen'}} />
			)}
			{/* lamp glow (behind the desk) */}
			<ellipse cx={1160} cy={600} rx={520} ry={340} fill="url(#warmGlow)" opacity={Math.min(1, lamp)} />
			{/* chair: seat and back, behind a seated character at x = 960 */}
			<g>
				<rect x={868} y={560} width={26} height={320} rx={6} fill="#6b4630" {...ink(3)} />
				<rect x={868} y={744} width={170} height={22} rx={6} fill="#7a5236" {...ink(3)} />
				<rect x={1012} y={766} width={18} height={114} fill="#6b4630" {...ink(2.5)} />
			</g>
			{/* desk and lamp */}
			<g>
				<rect x={1060} y={688} width={600} height={30} rx={8} fill="#9a6a42" {...ink(3.5)} />
				<rect x={1560} y={718} width={80} height={162} fill="#8a5c38" {...ink(3)} />
				<rect x={1080} y={718} width={22} height={162} fill="#8a5c38" {...ink(3)} />
				<path d="M1110,688 L1124,560 L1170,520" fill="none" stroke="#3b2a20" strokeWidth={7} strokeLinecap="round" />
				<path d="M1148,500 L1216,528 L1196,556 L1136,530 Z" fill="#3f7f86" {...ink(3)} />
				<ellipse cx={1110} cy={688} rx={34} ry={8} fill="#3b2a20" />
			</g>
		</g>
	);
};

export const location: Location = {
	id: 'arjun-room',
	interior: true,
	groundY: 880,
	backgroundGroundY: 800,
	propSlots: [[1230, 690], [1360, 690], [1480, 690], [1590, 690]],
	Background,
};
