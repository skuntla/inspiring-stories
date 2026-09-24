import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Defs, palette} from '../kit/style';
import type {Rig} from '../kit/types';
import {rig as meena} from '../series/quiet-lessons/characters/meena';
import {rig as meenaGrown} from '../series/quiet-lessons/characters/meena-grown';
import {rig as merchant} from '../series/quiet-lessons/characters/merchant';
import {rig as traveller} from '../series/quiet-lessons/characters/traveller';
import {rig as velu} from '../series/quiet-lessons/characters/velu';
import {rig as veluOld} from '../series/quiet-lessons/characters/velu-old';
import {rig as villager} from '../series/quiet-lessons/characters/villager';
import {Camel} from '../vendor/fluent-emoji/Camel';
import {Coin} from '../vendor/fluent-emoji/Coin';
import {MoneyBag} from '../vendor/fluent-emoji/MoneyBag';

// Model sheets for an episode's cast: each character full length with name and role, four
// expressions, and (PoseSheet) the lead's actions. Edit CAST / POSES for a new story.

type Entry = {rig: Rig; name: string; role: string; mood: string; head: [number, number, number]};
const CAST: Entry[] = [
	{rig: velu, name: 'Velu', role: 'digs for ten years', mood: 'calm', head: [8, -420, 105]},
	{rig: meena, name: 'Meena', role: 'the girl who believes', mood: 'happy', head: [6, -312, 92]},
	{rig: villager, name: 'Villager', role: 'the loudest mocker', mood: 'neutral', head: [10, -432, 112]},
	{rig: merchant, name: 'The Merchant', role: 'from the capital', mood: 'proud', head: [10, -436, 116]},
	{rig: traveller, name: 'The Traveller', role: 'tells the story onward', mood: 'thoughtful', head: [10, -426, 110]},
	{rig: meenaGrown, name: 'Meena, grown', role: 'keeps the records', mood: 'calm', head: [8, -424, 108]},
	{rig: veluOld, name: 'Velu, old', role: 'at the end of the road', mood: 'happy', head: [8, -420, 105]},
];
const EXPRESSIONS = ['happy', 'sad', 'surprised', 'worried'];
const PAPER = '#f3ecdc';
const INK = '#3b2a20';
const SERIF = 'Georgia, "Times New Roman", serif';

const pal = palette('morning');
const draw = (rig: Rig, stance: string, mood: string, t = 1.3, walkSpeed = 0) => (
	<rig.Component t={t} palette={pal} timeOfDay="morning" stance={stance} mood={mood} mouth="rest" eye={1}
		speaking={false} facing="right" walkSpeed={walkSpeed} />
);

const Headshot: React.FC<{e: Entry; mood: string; x: number; y: number; w: number}> = ({e, mood, x, y, w}) => {
	const [cx, cy, r] = e.head;
	return (
		<g>
			<rect x={x} y={y} width={w} height={w} rx={14} fill="#fbf7ee" stroke="#d9ccb0" strokeWidth={2} />
			<svg x={x} y={y} width={w} height={w} viewBox={`${cx - r} ${cy - r} ${2 * r} ${2 * r}`}>{draw(e.rig, 'stand', mood)}</svg>
			<text x={x + w / 2} y={y + w + 20} fontSize={15} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">{mood}</text>
		</g>
	);
};

const Title: React.FC<{title: string; sub: string}> = ({title, sub}) => (
	<g>
		<text x={60} y={78} fontSize={46} fontFamily={SERIF} fill={INK}>{title}</text>
		<text x={60} y={112} fontSize={22} fontFamily={SERIF} fontStyle="italic" fill="#7a6a58">{sub}</text>
		<path d="M60,132 L1860,132" stroke="#d9ccb0" strokeWidth={2} />
	</g>
);

export const CastSheet: React.FC = () => {
	const col = 1800 / CAST.length;
	return (
		<AbsoluteFill style={{backgroundColor: PAPER}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%">
				<Defs palette={pal} />
				<Title title="The Well at the End of the Road — cast" sub="Quiet Lessons · model sheet · faces, wardrobe and proportions" />
				{CAST.map((e, i) => {
					const cx = 60 + col * (i + 0.5);
					return (
						<g key={e.name}>
							<ellipse cx={cx} cy={612} rx={96} ry={12} fill="#d9ccb0" opacity={0.6} />
							<g transform={`translate(${cx - 18} 610) scale(0.9)`}>{draw(e.rig, 'stand', e.mood)}</g>
							<text x={cx} y={660} fontSize={26} fontFamily={SERIF} fontWeight={700} textAnchor="middle" fill={INK}>{e.name}</text>
							<text x={cx} y={688} fontSize={17} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">{e.role}</text>
							{EXPRESSIONS.map((m, j) => (
								<Headshot key={m} e={e} mood={m} x={cx - 118 + (j % 2) * 122} y={712 + Math.floor(j / 2) * 150} w={114} />
							))}
						</g>
					);
				})}
			</svg>
		</AbsoluteFill>
	);
};

// Velu's actions: the dig cycle (lift → strike), and the everyday stances, young and old.
const DIG_TIMES = [0, 0.25, 0.5, 0.8, 0.95];
export const PoseSheet: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: PAPER}}>
		<svg viewBox="0 0 1920 1080" width="100%" height="100%">
			<Defs palette={pal} />
			<Title title="Velu — actions" sub="the dig cycle, from strike to lift and back; everyday stances young and old" />
			{DIG_TIMES.map((t, i) => (
				<g key={t}>
					<path d={`M${130 + i * 250},560 L${370 + i * 250},560`} stroke="#b7a98f" strokeWidth={4} />
					<g transform={`translate(${200 + i * 250} 560) scale(0.78)`}>{draw(velu, 'dig', 'calm', t)}</g>
					<text x={250 + i * 250} y={600} fontSize={18} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">dig · {t.toFixed(2)} s</text>
				</g>
			))}
			<g transform="translate(1520 560) scale(0.78)">{draw(velu, 'dig', 'tired', 0.45)}</g>
			<text x={1560} y={600} fontSize={18} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">dig · tired (year seven)</text>
			{([['stand', 'proud', velu], ['walk', 'calm', velu], ['sit', 'thoughtful', velu], ['hold', 'happy', velu], ['reach', 'happy', velu],
				['stand', 'happy', veluOld], ['walk', 'calm', veluOld]] as [string, string, Rig][]).map(([stance, mood, rig], i) => (
				<g key={i}>
					{stance === 'sit' && <rect x={150 + i * 250 - 70} y={1010 - 92} width={170} height={16} rx={6} fill="#9a6a42" />}
					<g transform={`translate(${150 + i * 250} 1010) scale(0.72)`}>{draw(rig, stance, mood, 1.3, stance === 'walk' ? 100 : 0)}</g>
					<text x={170 + i * 250} y={1048} fontSize={18} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">
						{rig === veluOld ? 'old · ' : ''}{stance} / {mood}
					</text>
				</g>
			))}
		</svg>
	</AbsoluteFill>
);

// Props from Microsoft Fluent Emoji (MIT, render/src/vendor/fluent-emoji) with the series' ink outline,
// beside the cast for scale.
const COPPER = {'#F9C23C': '#d9894a', '#D3883E': '#a55a2c'};
export const PropSheet: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: PAPER}}>
		<svg viewBox="0 0 1920 1080" width="100%" height="100%">
			<Defs palette={pal} />
			<Title title="The Well at the End of the Road — props" sub="vendored from Fluent Emoji (MIT) with our ink outline; the copper coin is recoloured" />
			<g transform="translate(260 760) scale(0.95)">{draw(velu, 'hold', 'happy')}</g>
			<g transform="translate(372 530)"><Coin size={70} recolor={COPPER} /></g>
			<text x={320} y={820} fontSize={20} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">one copper coin</text>
			<g transform="translate(700 760) scale(0.95)">{draw(merchant, 'stand', 'proud')}</g>
			<g transform="translate(860 760)"><MoneyBag size={170} /></g>
			<text x={780} y={820} fontSize={20} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">the bag of gold</text>
			{[0, 1, 2].map((i) => (
				<g key={i} transform={`translate(${1180 + i * 250} ${760 - i * 40}) scale(${1 - i * 0.18})`}><Camel size={320} /></g>
			))}
			<text x={1420} y={820} fontSize={20} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">caravans on the road</text>
			<g transform="translate(560 1000)"><Coin size={110} /></g>
			<g transform="translate(700 1000)"><Coin size={110} recolor={COPPER} /></g>
			<text x={630} y={1050} fontSize={18} fontFamily={SERIF} fontStyle="italic" textAnchor="middle" fill="#7a6a58">original · copper</text>
		</svg>
	</AbsoluteFill>
);
