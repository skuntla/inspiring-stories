import React from 'react';
import {Mouth, moodFace} from './face';
import {INK, ink} from './style';
import type {RigProps} from './types';
import {type WalkFrame, knee, walkCycle} from './walk';

// A reusable "bean person": big round head, dot eyes, rounded torso, limb strokes and mitten hands,
// drawn three-quarter facing right with the origin between the feet. Characters differ only by a
// HumanSpec, a mix-and-match wardrobe in the spirit of Humaaans: hair style, facial hair, headwear,
// top, sleeves, lower garment (trousers, dhoti, sari, robe, long coat), sash, build and age.
// Standing height is about 470 px at size 1.

export type HumanSpec = {
	skin: string;
	skinShade: string;
	hair?: {color: string; greyTemples?: string; style?: 'short' | 'bun' | 'braids' | 'long' | 'fringe'; ribbon?: string};
	mustache?: {color: string; curled?: boolean};
	turban?: {color: string; shade: string; jewel?: string};
	bindi?: string;
	wrinkles?: boolean;
	stubble?: boolean;
	beard?: string; // colour of a full beard
	brows: string;
	browWidth?: number;
	shirt: string;
	shirtShade: string;
	sleeves: 'rolled' | 'long' | 'none';
	pants: string;
	shoes: string;
	apron?: string;
	hat?: {brim: string; crown: string; band: string};
	shaved?: string; // tone of a shaven scalp (no hair)
	robe?: {sash: string}; // a sash (or towel, or sari drape) over one shoulder; also draws the lower garment
	skirt?: {color: string; shade?: string; hem?: number}; // dhoti, sari, skirt or long coat; hem = y of its lower edge (ankle -48)
	buttons?: string; // a row of buttons down the front (a merchant's coat)
	stout?: boolean;
	size?: number; // overall scale: a child is about 0.72
	headScale?: number; // head size against the body: a child's is about 1.2
	stoop?: number; // degrees of forward lean when standing
};

type P = [number, number];
const HIP_Y = -186;
const SIT_DROP = 58; // how far the upper body drops when sitting (seat surface ~ 118 px above ground)

const limb = (a: P, b: P, bend: number, width: number, color: string) => {
	const mx = (a[0] + b[0]) / 2 + bend;
	const my = (a[1] + b[1]) / 2 + Math.abs(bend) * 0.4;
	const d = `M${a[0]},${a[1]} Q${mx},${my} ${b[0]},${b[1]}`;
	return (
		<g>
			<path d={d} fill="none" stroke={INK} strokeWidth={width + 6} strokeLinecap="round" />
			<path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round" />
		</g>
	);
};

const UPPER_ARM = 72;
const FOREARM = 70;

/** An arm: upper arm in the shirt colour, forearm in skin when sleeves are rolled.
 * The elbow comes from two-bone IK and always bends backward, like a real elbow. */
const arm = (spec: HumanSpec, shoulder: P, hand: P, fixedElbow?: P) => {
	// A hand raised above the shoulder in front of the body (the chin gesture) keeps its elbow forward
	// and low, so the forearm rises to the chin instead of crossing the mouth.
	const raisedInFront = hand[1] < shoulder[1] && hand[0] > shoulder[0] + 20;
	const elbow = fixedElbow ?? knee(shoulder, hand, UPPER_ARM, FOREARM, raisedInFront ? 1 : -1);
	return (
		<g>
			{limb(shoulder, elbow, 0, 28, spec.sleeves === 'none' ? spec.skin : spec.shirt)}
			{limb(elbow, hand, 0, 22, spec.sleeves === 'long' ? spec.shirt : spec.skin)}
			<circle cx={hand[0]} cy={hand[1]} r={15} fill={spec.skin} {...ink(3)} />
		</g>
	);
};

type Pose = {sit: boolean; lean: number; bow: number; hands: [P, P]; aim?: boolean; shovel?: [P, P]};

// Shoulders in the three-quarter view: the far one tucked behind the torso, the near one on the
// side of the body (not its front edge), so a hanging arm falls down the middle of the side.
const SHOULDERS: [P, P] = [[-22, -320], [8, -318]];
const ARM = UPPER_ARM + FOREARM - 8;
/** A hand hanging from a shoulder, swung by an angle in degrees (+ forward). */
const hang = (shoulder: P, degrees: number): P => {
	const a = (degrees * Math.PI) / 180;
	return [shoulder[0] + Math.sin(a) * ARM, shoulder[1] + Math.cos(a) * ARM];
};

const THIGH = 89.5; // thigh + shin = hip-to-foot height, so standing legs are straight
const SHIN = 89.5;

// Walk energy by mood: arm swing (degrees), extra slouch, and head bow.
const WALK_STYLE: Record<string, {swing: number; lean: number; bow: number}> = {
	happy: {swing: 30, lean: 1, bow: -3}, proud: {swing: 24, lean: 0, bow: -4}, calm: {swing: 14, lean: 2, bow: 0},
	thoughtful: {swing: 12, lean: 4, bow: 6}, sad: {swing: 8, lean: 8, bow: 12}, tired: {swing: 8, lean: 8, bow: 10},
	worried: {swing: 22, lean: 6, bow: 4}, scared: {swing: 26, lean: 6, bow: 2}, angry: {swing: 28, lean: 5, bow: 0},
};

/** Hands in body coordinates (seated poses already include the seat drop). */
// Head gestures stay beside the face (the temple, near the ear) or under it (the chin), never across
// the eyes or mouth, so expressions and lip sync stay readable.
const TEMPLE_SIT: P = [-24, -388];
const CHIN_SIT: P = [50, -282];
const TEMPLE_STAND: P = [-24, -446];
const CHIN_STAND: P = [50, -340];

// Archery: the far arm holds the bow out toward the target, the near hand draws the string back under
// the chin with the elbow high behind. Tense archers tremble; calm ones hold still.
const BOW_HAND: P = [118, -328];
const DRAW_HAND: P = [30, -346];
const DRAW_ELBOW: P = [-52, -334];

// Digging: both hands on a shovel that is lifted and driven down into the ground in a steady rhythm
// (a strike every DIG_PERIOD seconds). Tired or sad diggers are slower and lift less.
const DIG_PERIOD = 1.4;
/** 0 at the strike (blade in the ground) .. 1 fully lifted. */
export const digLift = (t: number, period = DIG_PERIOD) => {
	const u = (((t % period) + period) % period) / period;
	if (u < 0.6) return Math.sin((u / 0.6) * (Math.PI / 2)); // lift slowly
	if (u < 0.72) return Math.cos(((u - 0.6) / 0.12) * (Math.PI / 2)); // drive it down
	return 0; // the blade bites; a breath before the next lift
};

const lerp = (a: P, b: P, k: number): P => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k];

const pose = (stance: string, mood: string, walk: WalkFrame | null, t = 0): Pose => {
	const low = mood === 'sad' || mood === 'tired';
	switch (stance) {
		case 'dig': {
			const k = digLift(t, low ? DIG_PERIOD * 1.4 : DIG_PERIOD) * (low ? 0.7 : 1);
			// the back hand stays low at the hip; the lift raises the blade to about chest height
			const grip = lerp([-6, -246], [14, -286], k);
			const blade = lerp([172, -2], [214, -160], k);
			// grip and blade are in scene coordinates (the blade bites the ground at y 0); the rig turns
			// them into the leaning body's coordinates
			return {sit: false, lean: 12 - 6 * k, bow: 10 - 4 * k, hands: [grip, lerp(grip, blade, 0.42)], shovel: [grip, blade]};
		}
		case 'aim':
			return {sit: false, lean: mood === 'angry' || mood === 'worried' ? 4 : -2, bow: -2, hands: [BOW_HAND, DRAW_HAND], aim: true};
		case 'sit':
			if (low) return {sit: true, lean: 16, bow: 14, hands: [[62, -150], [86, -142]]};
			if (mood === 'worried') return {sit: true, lean: 10, bow: 8, hands: [[84, -152], TEMPLE_SIT]};
			if (mood === 'thoughtful') return {sit: true, lean: 8, bow: 4, hands: [[80, -150], CHIN_SIT]};
			if (mood === 'surprised') return {sit: true, lean: -5, bow: -6, hands: [[74, -160], [104, -168]]};
			if (mood === 'happy' || mood === 'proud') return {sit: true, lean: -3, bow: -2, hands: [[84, -152], [104, -150]]};
			return {sit: true, lean: 0, bow: 0, hands: [[84, -152], [104, -150]]};
		case 'hold':
			return {sit: false, lean: 2, bow: 0, hands: [[76, -262], [92, -256]]};
		case 'reach':
			return {sit: false, lean: 8, bow: 4, hands: [hang(SHOULDERS[0], -6), [150, -300]]};
		case 'walk': {
			// arms swing from the shoulder, opposite the legs: the far arm with the near leg
			const style = WALK_STYLE[mood] ?? {swing: 20, lean: 3, bow: 0};
			const s = walk ? walk.swing : 0;
			return {sit: false, lean: style.lean, bow: style.bow,
				hands: [hang(SHOULDERS[0], style.swing * s), hang(SHOULDERS[1], -style.swing * s)]};
		}
		default:
			if (low) return {sit: false, lean: 6, bow: 12, hands: [hang(SHOULDERS[0], 2), hang(SHOULDERS[1], 6)]};
			if (mood === 'worried') return {sit: false, lean: 5, bow: 6, hands: [hang(SHOULDERS[0], -4), TEMPLE_STAND]};
			if (mood === 'thoughtful') return {sit: false, lean: 2, bow: 4, hands: [hang(SHOULDERS[0], -4), CHIN_STAND]};
			if (mood === 'surprised') return {sit: false, lean: -4, bow: -6, hands: [hang(SHOULDERS[0], -18), hang(SHOULDERS[1], 22)]};
			if (mood === 'happy' || mood === 'proud') return {sit: false, lean: -3, bow: -3, hands: [hang(SHOULDERS[0], -6), hang(SHOULDERS[1], 2)]};
			return {sit: false, lean: 0, bow: 0, hands: [hang(SHOULDERS[0], -4), hang(SHOULDERS[1], 4)]};
	}
};

const Legs: React.FC<{spec: HumanSpec; sit: boolean; walk: WalkFrame | null}> = ({spec, sit, walk}) => {
	const lift = walk ? walk.bob : 0;
	const hips: [P, P] = [[-20, HIP_Y + (sit ? SIT_DROP : 0) + lift], [26, HIP_Y + (sit ? SIT_DROP : 0) + lift]];
	let feet: [P, P];
	let knees: [P, P];
	if (sit) {
		knees = [[74, hips[0][1] + 6], [100, hips[1][1] + 6]];
		feet = [[80, -8], [108, -6]];
	} else {
		// feet under the body; while walking they follow the planted-foot cycle
		const base: [P, P] = walk ? [[4, -8], [12, -8]] : [[-18, -8], [30, -8]];
		feet = walk
			? [[base[0][0] + walk.feet[0][0], base[0][1] + walk.feet[0][1]], [base[1][0] + walk.feet[1][0], base[1][1] + walk.feet[1][1]]]
			: base;
		knees = [knee(hips[0], feet[0], THIGH, SHIN), knee(hips[1], feet[1], THIGH, SHIN)];
	}
	// draw the far leg first so the near leg overlaps it
	return (
		<g>
			{[1, 0].map((i) => (
				<g key={i} opacity={i === 1 && walk ? 0.92 : 1}>
					{limb(hips[i], knees[i], 0, 36, spec.pants)}
					{limb(knees[i], feet[i], 0, 32, spec.pants)}
					<ellipse cx={feet[i][0] + 14} cy={feet[i][1] + 2} rx={28} ry={12} fill={spec.shoes} {...ink(3)} />
				</g>
			))}
		</g>
	);
};

/** The lower garment (robe, dhoti, sari, skirt or long coat): it sways with the stride, or drapes over
 * the lap when sitting. */
const RobeSkirt: React.FC<{spec: HumanSpec; sit: boolean; walk: WalkFrame | null}> = ({spec, sit, walk}) => {
	const color = spec.skirt?.color ?? spec.shirt;
	const shade = spec.skirt?.shade ?? spec.shirtShade;
	const hem = spec.skirt?.hem ?? -48;
	if (sit) {
		// a short garment (dhoti) rides up over the knees; a long one also hangs down the shins
		return (
			<g>
				<path d="M-54,-150 C-58,-118 -50,-104 -36,-100 L118,-104 C130,-106 132,-124 120,-138 L60,-152 Z" fill={color} {...ink(3)} />
				{hem > -80 && <path d="M92,-110 L128,-106 C130,-86 128,-56 126,-44 L90,-48 Z" fill={color} {...ink(3)} />}
			</g>
		);
	}
	const s = walk ? (walk.feet[0][0] - walk.feet[1][0]) * 0.18 : 0;
	const lift = walk ? walk.bob : 0;
	const flare = 10 + (hem + 200) * 0.1;
	return (
		<g transform={`translate(0 ${lift})`}>
			<path d={`M-54,-200 C-60,-150 ${-56 - flare * 0.8},${hem - 44} ${-56 - flare + s},${hem} Q${7 + s},${hem + 12} ${70 + flare + s},${hem} C${66 + flare * 0.8},${hem - 44} 70,-150 62,-200 Z`}
				fill={color} {...ink(3)} />
			<path d={`M4,-180 C2,-140 ${2 + s * 0.6},${hem - 40} ${4 + s},${hem - 2}`} fill="none" stroke={shade} strokeWidth={4} strokeLinecap="round" />
			<path d={`M36,-178 C40,-140 ${44 + s * 0.6},${hem - 42} ${50 + s},${hem - 4}`} fill="none" stroke={shade} strokeWidth={3} strokeLinecap="round" opacity={0.7} />
		</g>
	);
};

/** A shovel from the top grip to the blade tip. */
const Shovel: React.FC<{grip: P; blade: P}> = ({grip: [gx, gy], blade: [bx, by]}) => {
	const a = (Math.atan2(by - gy, bx - gx) * 180) / Math.PI;
	const len = Math.hypot(bx - gx, by - gy);
	return (
		<g transform={`translate(${gx} ${gy}) rotate(${a})`}>
			<path d={`M-6,0 L${len - 40},0`} stroke={INK} strokeWidth={14} strokeLinecap="round" />
			<path d={`M-6,0 L${len - 40},0`} stroke="#9a6a42" strokeWidth={8} strokeLinecap="round" />
			<path d={`M${len - 46},-22 L${len - 4},-18 Q${len + 8},0 ${len - 4},18 L${len - 46},22 Z`} fill="#8a8f96" {...ink(3)} />
			<path d="M-14,-12 L-14,12" stroke={INK} strokeWidth={8} strokeLinecap="round" />
		</g>
	);
};

/** A drawn bow with its string pulled to the draw hand and an arrow nocked. */
const Bow: React.FC<{bowHand: P; drawHand: P}> = ({bowHand: [hx, hy], drawHand: [dx, dy]}) => {
	const top: P = [hx - 34, hy - 150];
	const bottom: P = [hx - 34, hy + 150];
	const limbs = `M${top[0]},${top[1]} C${hx - 8},${hy - 124} ${hx + 8},${hy - 44} ${hx},${hy} C${hx + 8},${hy + 44} ${hx - 8},${hy + 124} ${bottom[0]},${bottom[1]}`;
	return (
		<g>
			<path d={`M${top[0]},${top[1]} L${dx},${dy} L${bottom[0]},${bottom[1]}`} fill="none" stroke="#efe6d0" strokeWidth={2.5} />
			<path d={limbs} fill="none" stroke={INK} strokeWidth={13} strokeLinecap="round" />
			<path d={limbs} fill="none" stroke="#8a5a2b" strokeWidth={8} strokeLinecap="round" />
			{/* the arrow, from the string to just past the bow */}
			<path d={`M${dx - 6},${dy} L${hx + 64},${hy - 2}`} stroke={INK} strokeWidth={6} strokeLinecap="round" />
			<path d={`M${dx - 6},${dy} L${hx + 64},${hy - 2}`} stroke="#d9c49a" strokeWidth={3} strokeLinecap="round" />
			<path d={`M${hx + 62},${hy - 10} L${hx + 84},${hy - 2} L${hx + 62},${hy + 6} Z`} fill="#6b6f76" {...ink(2)} />
			<path d={`M${dx - 4},${dy} l-18,-10 M${dx - 4},${dy} l-18,10`} stroke="#c8323a" strokeWidth={6} strokeLinecap="round" />
		</g>
	);
};

const Head: React.FC<{spec: HumanSpec; mood: string; mouth: RigProps['mouth']; eye: number; tilt: number}> = ({
	spec, mood, mouth, eye, tilt,
}) => {
	const face = moodFace(mood);
	const open = Math.max(0, Math.min(1, eye * face.lid));
	const O = ink(3.5);
	const eyeAt = (x: number, y: number, s: number) => (
		<g transform={`translate(${x} ${y}) scale(${face.eyeScale * s})`}>
			<ellipse cx={0} cy={0} rx={7} ry={9} fill="#1d1512" />
			<circle cx={2.4} cy={-3} r={2.6} fill="#ffffff" />
			<rect x={-9} y={-11} width={18} height={20 * (1 - open)} fill={spec.skin} />
		</g>
	);
	const brow = (x: number, s: number) => (
		<path d={`M${x - 11},-436 Q${x},-${442} ${x + 11},-436`} fill="none" stroke={spec.brows} strokeWidth={(spec.browWidth ?? 4) * s}
			strokeLinecap="round" transform={`translate(0 ${face.browLift}) rotate(${face.browTilt} ${x} -438)`} />
	);
	return (
		<g transform={`rotate(${tilt} 0 -360)`}>
			{/* neck */}
			<rect x={-14} y={-372} width={34} height={36} rx={10} fill={spec.skinShade} {...ink(3)} />
			{/* hair that falls behind the head */}
			{spec.hair?.style === 'long' && (
				<path d="M-58,-440 C-80,-400 -84,-340 -70,-300 C-50,-296 -30,-300 -20,-312 C-30,-350 -30,-390 -10,-430 Z" fill={spec.hair.color} {...O} />
			)}
			{spec.hair?.style === 'braids' && (
				<g>
					{[0, 1, 2, 3, 4].map((i) => (
						<ellipse key={i} cx={-48 - i * 2} cy={-392 + i * 24} rx={13} ry={15} fill={spec.hair!.color} {...ink(2.5)} />
					))}
					<path d="M-58,-278 l-16,-10 l2,20 Z M-58,-278 l16,-10 l-2,20 Z" fill={spec.hair.ribbon ?? '#c8323a'} {...ink(2)} />
				</g>
			)}
			{spec.hair?.style === 'bun' && <circle cx={-40} cy={-470} r={26} fill={spec.hair.color} {...O} />}
			{/* ear and head */}
			<ellipse cx={-44} cy={-410} rx={12} ry={16} fill={spec.skin} {...O} />
			<circle cx={8} cy={-418} r={64} fill={spec.skin} {...O} />
			{spec.shaved && (
				<path d="M-54,-424 C-58,-466 -22,-484 12,-482 C46,-480 68,-462 70,-436 C50,-446 30,-452 8,-450 C-14,-448 -34,-440 -54,-424 Z"
					fill={spec.shaved} opacity={0.35} />
			)}
			{spec.hair?.style === 'fringe' && (
				<path d="M-60,-392 C-72,-428 -58,-462 -26,-474 C-42,-452 -46,-424 -40,-398 C-46,-390 -54,-386 -60,-392 Z M52,-462 C60,-456 66,-446 68,-436 C62,-444 56,-450 48,-454 Z"
					fill={spec.hair.color} {...O} />
			)}
			{spec.hair && spec.hair.style !== 'fringe' && (
				<g>
					<path d="M-54,-420 C-60,-470 -20,-492 14,-490 C48,-488 70,-470 70,-440 C54,-452 34,-458 10,-456 C-12,-454 -30,-446 -38,-424 C-44,-414 -50,-410 -54,-420 Z"
						fill={spec.hair.color} {...O} />
					{spec.hair.greyTemples && <path d="M-40,-428 C-38,-440 -30,-448 -22,-450" stroke={spec.hair.greyTemples} strokeWidth={7} strokeLinecap="round" fill="none" />}
				</g>
			)}
			{spec.wrinkles && (
				<g fill="none" stroke={spec.skinShade} strokeWidth={3} strokeLinecap="round">
					<path d="M-8,-458 Q14,-464 38,-458 M0,-468 Q16,-472 32,-468" />
					<path d="M50,-424 l8,-4 M50,-414 l9,0" />
				</g>
			)}
			{spec.bindi && <circle cx={16} cy={-446} r={5} fill={spec.bindi} />}
			{spec.stubble && <path d="M-28,-380 C-10,-352 40,-348 64,-384" fill="none" stroke="#3a2f2a" strokeWidth={14} strokeLinecap="round" opacity={0.18} />}
			{spec.beard && (
				<path d="M-34,-392 C-40,-350 -10,-322 20,-322 C50,-322 72,-350 68,-392 C56,-372 40,-366 24,-366 C4,-366 -20,-372 -34,-392 Z"
					fill={spec.beard} {...O} />
			)}
			{/* cheek, eyes, brows, nose, mouth */}
			<ellipse cx={46} cy={-392} rx={11} ry={7} fill="#e08a7a" opacity={mood === 'happy' || mood === 'proud' ? 0.45 : 0.25} />
			{eyeAt(-2, -416, 0.85)}
			{eyeAt(34, -418, 1)}
			{brow(-2, 0.85)}
			{brow(34, 1)}
			{face.tear && <path d="M40,-402 q4,8 0,12 q-5,-3 0,-12 Z" fill="#a8d0ef" stroke="#6f9fc4" strokeWidth={1.5} />}
			<path d="M60,-414 Q74,-398 60,-392" fill={spec.skin} {...ink(3)} />
			{spec.mustache && (
				<g fill={spec.mustache.color} stroke={INK} strokeWidth={2}>
					<path d="M14,-392 C22,-402 36,-401 42,-395 C48,-401 60,-401 66,-390 C58,-386 48,-387 42,-391 C34,-386 22,-386 14,-392 Z" />
					{spec.mustache.curled && <path d="M14,-392 c-9,1 -12,-8 -5,-12 M66,-390 c9,1 11,-9 4,-12" fill="none" stroke={spec.mustache.color} strokeWidth={4} strokeLinecap="round" />}
				</g>
			)}
			<g transform={`translate(30 ${spec.beard ? -380 : -382}) scale(1.05)`}>
				<Mouth shape={mouth} mood={mood} />
			</g>
			{spec.turban && (
				<g>
					<path d="M-60,-428 C-70,-492 -24,-524 14,-522 C58,-520 84,-492 76,-436 C54,-452 32,-458 8,-456 C-18,-454 -42,-446 -60,-428 Z" fill={spec.turban.color} {...O} />
					<path d="M-54,-446 C-20,-470 40,-476 74,-452 M-46,-470 C-10,-492 40,-494 70,-474 M-30,-494 C0,-510 36,-510 58,-494"
						fill="none" stroke={spec.turban.shade} strokeWidth={5} strokeLinecap="round" />
					{spec.turban.jewel && (
						<g>
							<path d="M56,-482 C62,-512 76,-530 90,-540 C84,-520 72,-502 62,-478 Z" fill="#f4efe2" {...ink(2)} />
							<circle cx={58} cy={-474} r={10} fill={spec.turban.jewel} {...ink(2.5)} />
						</g>
					)}
				</g>
			)}
			{spec.hat && (
				<g>
					<path d="M-48,-452 C-46,-520 60,-524 64,-452 Z" fill={spec.hat.crown} {...O} />
					<path d="M-46,-462 C-10,-470 30,-470 62,-462 L64,-452 C30,-460 -10,-460 -48,-452 Z" fill={spec.hat.band} />
					<ellipse cx={8} cy={-452} rx={118} ry={22} fill={spec.hat.brim} {...O} />
				</g>
			)}
		</g>
	);
};

export const makeHuman = (spec: HumanSpec): React.FC<RigProps> => {
	const Human: React.FC<RigProps> = ({t, stance, mood, mouth, eye, speaking, walkSpeed}) => {
		const walk = stance === 'walk' ? walkCycle(t, walkSpeed ?? 0, 46, 22, 8) : null;
		const p = pose(stance, mood, walk, t);
		// calm and thoughtful characters breathe slower and deeper
		const breathe = mood === 'calm' || mood === 'thoughtful' ? Math.sin(t * 1.1) * 4 : Math.sin(t * 2) * 1.6;
		const bob = walk ? walk.bob : 0;
		const tilt = Math.sin(t * 1.2) * 1.2 + (speaking ? Math.sin(t * 6.8) * 1.8 : 0) + p.bow;
		const lean = p.lean + (spec.stoop ?? 0);
		const drop = p.sit ? SIT_DROP : 0;
		const shoulders = SHOULDERS;
		// a tense archer's hands shake; a calm one's are still
		const shake = p.aim && (mood === 'angry' || mood === 'worried') ? 1 : 0;
		const bowHand: P = [p.hands[0][0] + Math.sin(t * 29) * 2.5 * shake, p.hands[0][1] + Math.sin(t * 23 + 1) * 3 * shake];
		const drawHand: P = [p.hands[1][0] + Math.sin(t * 31 + 2) * 2 * shake, p.hands[1][1] + Math.sin(t * 27) * 2.5 * shake];
		// scene → leaning body: undo the lean around the hip so the shovel's blade meets the real ground
		const unlean = ([x, y]: P): P => {
			const a = (-lean * Math.PI) / 180;
			const dy = y - HIP_Y;
			return [x * Math.cos(a) - dy * Math.sin(a), HIP_Y + x * Math.sin(a) + dy * Math.cos(a)];
		};
		if (spec.headScale && !p.aim && !p.shovel) {
			const hs = spec.headScale;
			p.hands = p.hands.map(([x, y]) => (y < -330 ? [8 + (x - 8) * hs, -345 + (y + 345) * hs] : [x, y])) as [P, P];
		}
		if (p.shovel) {
			p.shovel = [unlean(p.shovel[0]), unlean(p.shovel[1])];
			p.hands = [p.shovel[0], lerp(p.shovel[0], p.shovel[1], 0.42)];
		}
		return (
			<g filter="url(#softEdge)" transform={spec.size ? `scale(${spec.size})` : undefined}>
				<ellipse cx={20} cy={4} rx={110} ry={14} fill="#3d3a2c" opacity={0.22} />
				<Legs spec={spec} sit={p.sit} walk={walk} />
				{(spec.robe || spec.skirt) && <RobeSkirt spec={spec} sit={p.sit} walk={walk} />}
				<g transform={`translate(0 ${drop + bob}) rotate(${lean} 0 ${HIP_Y})`}>
					{arm(spec, shoulders[0], p.aim ? bowHand : [p.hands[0][0], p.hands[0][1] - drop])}
					<g transform={`translate(0 ${breathe * 0.4})`}>
						<g transform={spec.stout ? 'translate(5 -176) scale(1.22 1) translate(-5 176)' : undefined}>
							<path d={spec.stout
								? 'M-50,-338 C-66,-300 -70,-220 -54,-176 C-20,-164 30,-164 60,-176 C76,-220 72,-300 52,-338 C20,-352 -18,-352 -50,-338 Z'
								: 'M-50,-338 C-62,-300 -64,-230 -54,-176 C-20,-166 30,-166 60,-176 C68,-230 66,-300 52,-338 C20,-352 -18,-352 -50,-338 Z'}
								fill={spec.shirt} {...ink(3.5)} />
						</g>
						{spec.buttons && [0, 1, 2, 3].map((i) => <circle key={i} cx={24} cy={-318 + i * 34} r={5} fill={spec.buttons} {...ink(1.5)} />)}
						<path d="M-10,-346 L6,-318 L22,-346" fill="none" stroke={spec.shirtShade} strokeWidth={4} strokeLinejoin="round" />
						{spec.robe && (
							<path d="M-34,-340 C-10,-300 20,-250 50,-182 L66,-190 C40,-252 12,-306 -14,-346 Z" fill={spec.robe.sash} {...ink(3)} />
						)}
						{spec.apron && (
							<path d="M-30,-300 C-34,-240 -40,-150 -38,-96 L66,-96 C68,-150 62,-240 58,-300 Z" fill={spec.apron} {...ink(3)} />
						)}
					</g>
					<g transform={spec.headScale ? `translate(8 -345) scale(${spec.headScale}) translate(-8 345)` : undefined}>
						<Head spec={spec} mood={mood} mouth={mouth} eye={eye} tilt={tilt} />
					</g>
					{p.aim && <Bow bowHand={bowHand} drawHand={drawHand} />}
					{p.shovel && <Shovel grip={p.shovel[0]} blade={p.shovel[1]} />}
					{p.aim
						? arm(spec, shoulders[1], drawHand, [DRAW_ELBOW[0] + drawHand[0] - DRAW_HAND[0], DRAW_ELBOW[1] + drawHand[1] - DRAW_HAND[1]])
						: arm(spec, shoulders[1], [p.hands[1][0], p.hands[1][1] - drop])}
				</g>
			</g>
		);
	};
	return Human;
};
