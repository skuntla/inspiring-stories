import React from 'react';
import {ink, rand} from '../../kit/style';

// Shared drawing for the archery close-ups: a straw target seen close, the courtyard blurred behind,
// a corner flag and wind streaks that show gusts, and arrows in flight. The locations in
// common/locations decide when arrows fly; this file decides how they look and move.

type P = [number, number];
export const CENTER: P = [1180, 470];
const START: P = [-300, 560];
const FLIGHT = 1.1; // seconds from the left edge to the target

const windAt = (t: number) => 0.55 + 0.25 * Math.sin(t * 0.63) + 0.2 * Math.max(0, Math.sin(t * 1.7 + 1)) ** 3;
const smooth = (x: number) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

export const Backdrop: React.FC<{t: number}> = ({t}) => {
	const w = windAt(t);
	const wave = (u: number) => Math.sin(u * 6 - t * (6 + 5 * w)) * (8 + 12 * w) * u;
	const flag = Array.from({length: 9}, (_, i) => i / 8);
	return (
		<g>
			<g filter="url(#farBlur)">
				<path d="M-240,640 L300,470 L620,600 L980,420 L1400,590 L1800,450 L2160,620 L2160,900 L-240,900 Z" fill="#a9b6c4" opacity={0.8} />
				<rect x={-240} y={700} width={2400} height={90} fill="#b7a98f" />
				<rect x={-240} y={780} width={2400} height={520} fill="#cbbd9f" />
				{/* the corner flag, soft and out of focus */}
				<path d={`M1720,60 ${flag.map((u) => `L${1720 + u * 300},${60 + (1 - w) * 50 * u + wave(u)}`).join(' ')} ${flag
					.slice()
					.reverse()
					.map((u) => `L${1720 + u * 290},${190 + (1 - w) * 60 * u + wave(u)}`)
					.join(' ')} Z`} fill="#c8323a" />
				<rect x={1700} y={40} width={16} height={900} fill="#6b4a2e" />
			</g>
			{/* target stand */}
			<path d="M1040,640 L940,1060 M1320,640 L1420,1060 M1180,700 L1240,1060" stroke="#6b4a2e" strokeWidth={26} strokeLinecap="round" />
			<path d="M1040,640 L940,1060 M1320,640 L1420,1060 M1180,700 L1240,1060" stroke={'#3b2a20'} strokeWidth={4} strokeLinecap="round" opacity={0.4} />
			{/* the target */}
			<g>
				<ellipse cx={CENTER[0] + 16} cy={CENTER[1] + 12} rx={262} ry={282} fill="#9c8a5e" {...ink(4)} />
				<ellipse cx={CENTER[0]} cy={CENTER[1]} rx={262} ry={282} fill="#e8d9ae" {...ink(4)} />
				{Array.from({length: 40}).map((_, i) => (
					<path key={i} d={`M${CENTER[0] - 250 + rand(i, 41) * 500},${CENTER[1] - 250 + rand(i, 43) * 500} l${-8 + rand(i, 47) * 16},${10}`}
						stroke="#c9b27a" strokeWidth={3} strokeLinecap="round" />
				))}
				<ellipse cx={CENTER[0]} cy={CENTER[1]} rx={200} ry={216} fill="#c8323a" {...ink(2.5)} />
				<ellipse cx={CENTER[0]} cy={CENTER[1]} rx={140} ry={151} fill="#f4efe2" {...ink(2.5)} />
				<ellipse cx={CENTER[0]} cy={CENTER[1]} rx={80} ry={86} fill="#c8323a" {...ink(2.5)} />
				<ellipse cx={CENTER[0]} cy={CENTER[1]} rx={30} ry={32} fill="#e9c046" {...ink(2.5)} />
			</g>
		</g>
	);
};

/** White wind streaks sweeping across the frame around time `at` (a gust), or gently all the time. */
export const WindStreaks: React.FC<{t: number; at?: number[]; gentle?: boolean}> = ({t, at = [], gentle}) => {
	const gusts = gentle ? [...at, ...[0, 1, 2, 3, 4, 5, 6, 7].map((k) => k * 2.6 + 0.4)] : at;
	return (
		<g>
			{gusts.map((g, gi) => {
				const u = (t - g + 0.25) / 1.1;
				if (u < 0 || u > 1) return null;
				const strong = at.includes(g);
				return Array.from({length: strong ? 6 : 3}).map((_, i) => {
					const y = 180 + rand(i + gi * 7, 91) * 640;
					const x = -500 + u * 2900 + rand(i, 93) * 300;
					return (
						<path key={`${gi}-${i}`} d={`M${x},${y} q180,-30 360,0 t360,-6`} fill="none" stroke="#ffffff" strokeWidth={strong ? 7 : 4}
							strokeLinecap="round" opacity={Math.sin(Math.PI * u) * (strong ? 0.75 : 0.35)} />
					);
				});
			})}
		</g>
	);
};

const Arrow: React.FC<{at: P; angle: number; buried?: boolean}> = ({at: [x, y], angle, buried}) => (
	<g transform={`translate(${x} ${y}) rotate(${(angle * 180) / Math.PI})`}>
		{buried && <ellipse cx={0} cy={0} rx={7} ry={10} fill="#3b2a20" opacity={0.5} />}
		<path d="M-330,0 L0,0" stroke="#3b2a20" strokeWidth={13} strokeLinecap="round" />
		<path d="M-330,0 L0,0" stroke="#d9c49a" strokeWidth={7} strokeLinecap="round" />
		{!buried && <path d="M-6,-16 L40,0 L-6,16 Z" fill="#6b6f76" {...ink(3)} />}
		<path d="M-300,0 L-340,-26 L-272,0 L-340,26 Z" fill="#c8323a" {...ink(2.5)} />
	</g>
);

/** An arrow launched at `launch` that a gust at `launch + gustAfter` turns away above the target. */
export const BlownArrow: React.FC<{t: number; launch: number; gustAfter: number; seed: number}> = ({t, launch, gustAfter, seed}) => {
	const tau = t - launch;
	if (tau < 0 || tau > 2.4) return null;
	const heading0 = Math.atan2(CENTER[1] - START[1], CENTER[0] - START[0]);
	const speed = Math.hypot(CENTER[0] - START[0], CENTER[1] - START[1]) / FLIGHT;
	const turnTo = -(0.55 + rand(seed, 97) * 0.35); // up and away
	const heading = (s: number) => heading0 + turnTo * smooth((s - gustAfter) / 0.45);
	let [x, y] = START;
	const dt = 1 / 120;
	for (let s = 0; s < tau; s += dt) {
		x += Math.cos(heading(s)) * speed * dt;
		y += Math.sin(heading(s)) * speed * dt;
	}
	const flutter = Math.sin(tau * 38) * 0.05 * smooth((tau - gustAfter) / 0.2);
	return <Arrow at={[x, y]} angle={heading(tau) + flutter} />;
};

/** An arrow aimed a little upwind that the wind curves in to land close to the center at `land`.
 * It leaves early in the shot and flies slower when the landing word comes late: a slow-motion shot. */
export const CurvingArrow: React.FC<{t: number; land: number; miss?: P}> = ({t, land, miss = [-34, 40]}) => {
	const launch = Math.max(0.15, land - 2.4);
	if (t < launch) return null;
	const end: P = [CENTER[0] + miss[0], CENTER[1] + miss[1]];
	const ctrl: P = [(START[0] + end[0]) / 2, Math.min(START[1], end[1]) - 260]; // aimed high, pushed back down
	const u = Math.min(1, (t - launch) / (land - launch));
	const bez = (a: number, b: number, c: number) => (1 - u) * (1 - u) * a + 2 * u * (1 - u) * b + u * u * c;
	const pos: P = [bez(START[0], ctrl[0], end[0]), bez(START[1], ctrl[1], end[1])];
	const tangent = Math.atan2(2 * (1 - u) * (ctrl[1] - START[1]) + 2 * u * (end[1] - ctrl[1]), 2 * (1 - u) * (ctrl[0] - START[0]) + 2 * u * (end[0] - ctrl[0]));
	const after = t - land;
	const quiver = after > 0 ? Math.sin(after * 42) * 0.06 * Math.exp(-after * 3) : 0;
	// once it lands, the head is buried in the straw
	return <Arrow at={pos} angle={tangent + quiver} buried={after > 0} />;
};

/** A still emblem of the story's problem for thumbnails: a target, and an arrow bending away from it
 * in the wind, with its path traced and wind streaks. Drawn around (0, 0) at about 700 × 500. */
export const WindMissEmblem: React.FC = () => (
	<g>
		<path d="M-40,140 L-80,300 M60,140 L100,300 M10,160 L40,300" stroke="#6b4a2e" strokeWidth={18} strokeLinecap="round" />
		<ellipse cx={10} cy={20} rx={150} ry={162} fill="#e8d9ae" {...ink(5)} />
		<ellipse cx={10} cy={20} rx={112} ry={122} fill="#c8323a" {...ink(3)} />
		<ellipse cx={10} cy={20} rx={74} ry={80} fill="#f4efe2" {...ink(3)} />
		<ellipse cx={10} cy={20} rx={36} ry={40} fill="#c8323a" {...ink(3)} />
		<ellipse cx={10} cy={20} rx={13} ry={14} fill="#e9c046" {...ink(2)} />
		{/* the arrow's path: straight for the center, then bent up and away by the wind */}
		<path d="M-440,230 C-300,180 -200,140 -160,80 C-120,20 20,-190 190,-300" fill="none" stroke="#ffffff" strokeWidth={10}
			strokeDasharray="4 22" strokeLinecap="round" opacity={0.9} />
		{[0, 1, 2].map((i) => (
			<path key={i} d={`M${-340 + i * 40},${-40 - i * 70} q120,-30 240,0 t240,-8`} fill="none" stroke="#ffffff" strokeWidth={9 - i * 2}
				strokeLinecap="round" opacity={0.85 - i * 0.2} />
		))}
		<g transform="translate(360 -390) rotate(-40)">
			<path d="M-260,0 L0,0" stroke="#3b2a20" strokeWidth={14} strokeLinecap="round" />
			<path d="M-260,0 L0,0" stroke="#d9c49a" strokeWidth={8} strokeLinecap="round" />
			<path d="M-6,-18 L44,0 L-6,18 Z" fill="#6b6f76" {...ink(3)} />
			<path d="M-232,0 L-276,-28 L-202,0 L-276,28 Z" fill="#c8323a" {...ink(2.5)} />
		</g>
	</g>
);
