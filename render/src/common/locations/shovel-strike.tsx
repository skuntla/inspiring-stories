import React from 'react';
import {wordAt} from '../../kit/spoken';
import {ink, rand} from '../../kit/style';
import type {DrawContext, Location} from '../../kit/types';

// Close on hard ground at the bottom of a pit: an iron shovel strikes again and again, throwing sparks
// and dust. When the voice says "crack…" the rock splits; on "water" (or "spring") clear water wells up
// through the crack and the striking stops. Without those words it simply keeps striking (a hook).
export const about = "Close-up of a shovel striking hard rock, sparks and dust; on 'cracked' the rock splits and on 'water' a spring bursts up.";

const PERIOD = 1.4;
const HIT = 0.72; // fraction of the period when the blade lands

const Background: React.FC<DrawContext> = ({t, words}) => {
	const crackAt = wordAt(words, /^crack/i);
	const waterAt = wordAt(words, /^(water|spring)/i) ?? (crackAt !== undefined ? crackAt + 1.2 : undefined);
	const stopAt = crackAt ?? Infinity;
	// the swing: 0 raised .. 1 landed (at phase HIT); after the crack the shovel rests in the ground
	const ph = ((((t - 0.3) % PERIOD) + PERIOD) % PERIOD) / PERIOD;
	const swing = t >= stopAt ? 1 : ph < 0.6 ? 1 - Math.sin((ph / 0.6) * (Math.PI / 2)) : ph < HIT ? (ph - 0.6) / (HIT - 0.6) : 1;
	const hitAge = t < 0.3 || t >= stopAt || ph < HIT ? -1 : (ph - HIT) * PERIOD;
	const crack = crackAt === undefined ? 0 : Math.max(0, Math.min(1, (t - crackAt) / 0.5));
	const water = waterAt === undefined ? 0 : Math.max(0, Math.min(1, (t - waterAt) / 1.6));
	return (
		<g>
			<rect x={-240} y={-240} width={2400} height={1560} fill="#3a2a1e" />
			<path d="M-240,-240 L500,-240 L380,1300 L-240,1300 Z" fill="#2c2018" />
			<path d="M2160,-240 L1450,-240 L1560,1300 L2160,1300 Z" fill="#2c2018" />
			<path d="M620,-240 L1300,-240 L1500,700 L420,700 Z" fill="#fff4d6" opacity={0.06} />
			{/* the rock floor */}
			<path d="M-240,640 C400,600 1500,610 2160,650 L2160,1300 L-240,1300 Z" fill="#6b5240" />
			{Array.from({length: 22}).map((_, i) => (
				<ellipse key={i} cx={rand(i, 581) * 1920} cy={680 + rand(i, 583) * 500} rx={20 + rand(i, 585) * 40} ry={10 + rand(i, 587) * 10}
					fill="#7d6250" {...ink(2, 0.5)} />
			))}
			{/* the crack, growing out from the strike point */}
			{crack > 0 && (
				<path d={`M960,760 L${960 - 180 * crack},${780 + 40 * crack} M960,760 L${960 + 220 * crack},${740 + 60 * crack} M960,760 L${930 + 20 * crack},${760 + 200 * crack}`}
					fill="none" stroke="#1d140e" strokeWidth={10} strokeLinecap="round" />
			)}
			{/* water welling up */}
			{water > 0 && (
				<g>
					<ellipse cx={960} cy={790} rx={60 + 700 * water} ry={14 + 90 * water} fill="#3f7fa6" opacity={0.9} />
					<ellipse cx={960} cy={780} rx={40 + 520 * water} ry={8 + 60 * water} fill="#8fc3e0" opacity={0.6} />
					{Array.from({length: 14}).map((_, i) => {
						const a = -Math.PI * (0.15 + rand(i, 589) * 0.7);
						const k = ((t * 1.5 + rand(i, 591)) % 1);
						const r = 60 + 260 * k * (0.6 + 0.4 * water);
						return <circle key={i} cx={960 + Math.cos(a) * r} cy={770 + Math.sin(a) * r * 0.9 + k * k * 160} r={9 - k * 6} fill="#cfe8f5" opacity={(1 - k) * water} />;
					})}
					{[0, 1, 2].map((i) => {
						const k = ((t * 0.6 + i / 3) % 1);
						return <ellipse key={`r${i}`} cx={960} cy={790} rx={80 + 600 * k * water} ry={10 + 70 * k * water} fill="none" stroke="#e6f4fb" strokeWidth={3} opacity={(1 - k) * water} />;
					})}
				</g>
			)}
			{/* sparks and dust at each strike */}
			{hitAge >= 0 && hitAge < 0.5 && (
				<g>
					{Array.from({length: 10}).map((_, i) => {
						const a = -Math.PI * (0.1 + rand(i, 593) * 0.8);
						const r = 30 + 260 * hitAge;
						return <path key={i} d={`M${960 + Math.cos(a) * r},${750 + Math.sin(a) * r} l${Math.cos(a) * 18},${Math.sin(a) * 18}`} stroke="#ffd98a"
							strokeWidth={5} strokeLinecap="round" opacity={1 - hitAge * 2} />;
					})}
					<ellipse cx={960} cy={740} rx={80 + 300 * hitAge} ry={30 + 80 * hitAge} fill="#c9b08a" opacity={0.5 * (1 - hitAge * 2)} />
				</g>
			)}
			{/* the shovel: from above right, rising and driving down */}
			<g transform={`translate(${960 + (1 - swing) * 260} ${760 - (1 - swing) * 420}) rotate(${-38 + (1 - swing) * 22})`}>
				<path d="M0,-40 L0,-900" stroke="#3b2a20" strokeWidth={34} strokeLinecap="round" />
				<path d="M0,-40 L0,-900" stroke="#9a6a42" strokeWidth={22} strokeLinecap="round" />
				<path d="M-78,-150 L78,-150 L66,-10 Q0,30 -66,-10 Z" fill="#7d8288" {...ink(5)} />
				<path d="M-40,-110 L30,-70" stroke="#a0662e" strokeWidth={9} opacity={0.5} />
			</g>
		</g>
	);
};

export const location: Location = {id: 'shovel-strike', interior: true, groundY: 1040, propSlots: [], Background};
