import React from 'react';
import {ink, rand} from '../../kit/style';
import type {DrawContext, Location} from '../../kit/types';

export const about = "Close-up of dry, cracked soil darkening as water pours onto it from a can; a sprout tip shows at the end.";

// Close on dry, cracked soil: a stream of water falls from the can's spout, drops splash, and the
// soil darkens where it lands; a tiny sprout tip begins to show near the end.
const Background: React.FC<DrawContext> = ({t}) => {
	const wet = Math.min(1, t / 2.6);
	return (
		<g>
			<rect x={-200} y={-200} width={2320} height={1480} fill="#caa27a" />
			<ellipse cx={960} cy={520} rx={900} ry={520} fill="#e8b878" opacity={0.25} />
			{Array.from({length: 26}).map((_, i) => {
				const x = -100 + rand(i, 3) * 2100;
				const y = 380 + rand(i, 4) * 700;
				return <path key={i} d={`M${x},${y} l${40 + rand(i, 5) * 60},${-20 + rand(i, 6) * 40} l${30 + rand(i, 7) * 40},${10 + rand(i, 8) * 30}`}
					fill="none" stroke="#9c7650" strokeWidth={4} strokeLinecap="round" />;
			})}
			{/* the wet patch spreading */}
			<ellipse cx={980} cy={760} rx={120 + 380 * wet} ry={50 + 150 * wet} fill="#6e4a30" opacity={0.75 * wet} filter="url(#blur8)" />
			{/* spout and stream */}
			<g transform="translate(1500 -40) rotate(24)">
				<rect x={-60} y={0} width={360} height={60} rx={18} fill="#5f8a44" {...ink(3)} />
				<ellipse cx={-60} cy={30} rx={26} ry={44} fill="#4f7a3a" {...ink(3)} />
			</g>
			<path d="M1440,40 C1300,200 1120,500 1000,740" fill="none" stroke="#9fd0f0" strokeWidth={14} strokeLinecap="round" opacity={0.75} />
			{Array.from({length: 24}).map((_, i) => {
				const k = (t * 1.6 + i / 24) % 1;
				const x = 1440 - 440 * k + Math.sin(i) * 14;
				const y = 40 + 700 * k * k;
				return <circle key={i} cx={x} cy={y} r={7} fill="#cfe9fb" opacity={0.9} />;
			})}
			{Array.from({length: 10}).map((_, i) => {
				const k = (t * 1.3 + i / 10) % 1;
				const a = (i / 10) * Math.PI;
				return <circle key={`s${i}`} cx={1000 + Math.cos(a) * 120 * k} cy={740 - Math.sin(a) * 60 * k + 80 * k * k} r={6 * (1 - k)} fill="#cfe9fb" />;
			})}
			{/* a tiny sprout tip appears as the soil softens */}
			{t > 2.8 && (
				<g transform={`translate(900 780) scale(${Math.min(1, (t - 2.8) / 1.2)})`}>
					<path d="M0,0 C-4,-20 6,-34 0,-46" fill="none" stroke="#4f7a3a" strokeWidth={8} strokeLinecap="round" />
					<ellipse cx={4} cy={-50} rx={14} ry={9} fill="#7cba5a" {...ink(2)} />
				</g>
			)}
		</g>
	);
};

export const location: Location = {id: 'watering-closeup', interior: true, groundY: 880, propSlots: [], Background};
