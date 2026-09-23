import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {registry} from './generated/registry';
import {ATMOSPHERE} from './kit/atmosphere';
import {Captions} from './kit/Captions';
import {Defs, Sky, ease, palette} from './kit/style';
import type {CastMember, DrawContext, Shape, Shot, SpokenWord, Timeline, View} from './kit/types';

const FADE = 8; // frames of fade at each shot boundary
const BLINK = [0.55, 0.1, 0, 0.15, 0.6, 1];

const mouthAt = (c: CastMember, f: number): Shape => {
	let shape: Shape = 'rest';
	for (const [frame, s] of c.mouth) {
		if (frame > f) break;
		shape = s;
	}
	return shape;
};

const eyeAt = (c: CastMember, f: number) => {
	for (const b of c.blinks) {
		const d = f - b;
		if (d >= 0 && d < BLINK.length) return BLINK[d];
	}
	return 1;
};

const FRAMING = {medium: {zoom: 1.55, head: 0.6}, close: {zoom: 2.3, head: 0.8}};
const SIT_DROP = 58; // how far a seated human's head is below its standing height (kit/human.tsx)

/** The view a shot is built around: the whole scene, or the subject's face for medium/close shots. */
const baseView = (shot: Shot, f: number): View => {
	const {framing, subject} = shot.camera;
	if (framing === 'wide' || !subject) return [960, 540, 1];
	const rig = registry.characters[subject.id];
	const location = registry.locations[shot.location];
	const member = shot.cast.find((c) => c.id === subject.id);
	const ground = subject.depth < 1 ? location.backgroundGroundY ?? location.groundY - 140 : location.groundY;
	const sitting = member?.stance === 'sit' || member?.stance === 'kneel' ? SIT_DROP : 0;
	const {zoom, head} = FRAMING[framing];
	const x = member?.travel
		? member.travel.from + (member.travel.to - member.travel.from) * Math.min(1, f / Math.max(1, shot.frames - 1))
		: subject.x;
	const look = subject.facing === 'right' ? 1 : subject.facing === 'left' ? -1 : 0; // leave room in front of the face
	return [x + (look * 140) / zoom, ground - (rig.height * head - sitting) * subject.depth, zoom];
};

const view = (shot: Shot, f: number): View => {
	const e = ease(Math.min(1, f / Math.max(1, shot.frames - 1)));
	const [a, b] = [shot.camera.from, shot.camera.to];
	const [bx, by, bz] = baseView(shot, f);
	const z = bz * (a[2] + (b[2] - a[2]) * e);
	const hw = 960 / z;
	const hh = 540 / z;
	const cx = Math.min(Math.max(bx + a[0] + (b[0] - a[0]) * e, hw), 1920 - hw);
	const cy = Math.min(Math.max(by + a[1] + (b[1] - a[1]) * e, hh), 1080 - hh);
	return [cx, cy, z];
};

/** Every word spoken in the shot, in seconds from its start, in order. */
const spokenWords = (shot: Shot, fps: number): SpokenWord[] =>
	shot.captions.flatMap((p) => p.words.map(([text, from, to]) => ({text, from: from / fps, to: to / fps, speaker: p.speaker})));

const ShotScene: React.FC<{shot: Shot; f: number; fps: number}> = ({shot, f, fps}) => {
	const location = registry.locations[shot.location];
	const pal = palette(shot.timeOfDay);
	const words = React.useMemo(() => spokenWords(shot, fps), [shot, fps]);
	const ctx: DrawContext = {t: f / fps, palette: pal, timeOfDay: shot.timeOfDay, words};
	const [cx, cy, z] = view(shot, f);

	// props: each character holding something takes the next prop; the rest fill the location's slots
	const queue = [...shot.props];
	const held = new Map<string, string>();
	for (const c of shot.cast) if (c.stance === 'hold' && queue.length) held.set(c.id, queue.shift()!);
	const free = queue.slice(0, location.propSlots.length);
	const cast = [...shot.cast].sort((a, b) => a.depth - b.depth);

	return (
		<svg viewBox="0 0 1920 1080" width="100%" height="100%" style={{position: 'absolute'}}>
			<Defs palette={pal} />
			<g transform={`translate(960 540) scale(${z.toFixed(4)}) translate(${(-cx).toFixed(2)} ${(-cy).toFixed(2)})`}>
				{!location.interior && <Sky palette={pal} />}
				<location.Background {...ctx} />
				{shot.atmosphere.map((a) => {
					const Overlay = ATMOSPHERE[a];
					return Overlay ? <Overlay key={`b-${a}`} t={ctx.t} palette={pal} layer="back" /> : null;
				})}
				{free.map((id, i) => {
					const P = registry.props[id];
					const [x, y] = location.propSlots[i];
					return (
						<g key={id} transform={`translate(${x} ${y})`}>
							<P.Component {...ctx} />
						</g>
					);
				})}
				{cast.map((c) => {
					const rig = registry.characters[c.id];
					const ground = c.depth < 1 ? location.backgroundGroundY ?? location.groundY - 140 : location.groundY;
					const flip = c.facing === 'left' ? -1 : 1;
					const x = c.travel ? c.travel.from + (c.travel.to - c.travel.from) * Math.min(1, f / Math.max(1, shot.frames - 1)) : c.x;
					const mouth = mouthAt(c, f);
					const prop = held.get(c.id);
					const P = prop ? registry.props[prop] : undefined;
					return (
						<g key={c.id} transform={`translate(${x} ${ground}) scale(${flip * c.depth} ${c.depth})`}>
							<rig.Component {...ctx} stance={c.stance} mood={c.mood} mouth={mouth} eye={eyeAt(c, f)}
								speaking={mouth !== 'rest'} facing={c.facing} walkSpeed={c.travel ? c.travel.speed / c.depth : 0} />
							{P && (
								<g transform={`translate(${rig.anchors.hand[0]} ${rig.anchors.hand[1]})`}>
									<P.Component {...ctx} />
								</g>
							)}
						</g>
					);
				})}
				{location.Foreground && <location.Foreground {...ctx} />}
				{shot.atmosphere.map((a) => {
					const Overlay = ATMOSPHERE[a];
					return Overlay ? <Overlay key={`f-${a}`} t={ctx.t} palette={pal} layer="front" /> : null;
				})}
			</g>
			{/* light of the time of day, paper grain and vignette stay fixed to the frame */}
			<rect width={1920} height={1080} fill={pal.tint} opacity={pal.tintOpacity} style={{mixBlendMode: 'multiply'}} />
			<rect width={1920} height={1080} filter="url(#paper)" opacity={0.06} style={{mixBlendMode: 'multiply'}} />
			<rect width={1920} height={1080} fill="url(#vignette)" />
			<rect width={1920} height={1080} fill="#000" opacity={Math.max(0, 1 - Math.min(f, shot.frames - 1 - f) / FADE)} />
		</svg>
	);
};

export const Episode: React.FC<{timeline: Timeline}> = ({timeline}) => {
	const frame = useCurrentFrame();
	const shot = timeline.shots.find((s) => frame >= s.from && frame < s.from + s.frames) ?? timeline.shots[timeline.shots.length - 1];
	const f = frame - shot.from;
	return (
		<AbsoluteFill style={{backgroundColor: '#000'}}>
			{timeline.audio.src && <Audio src={staticFile(timeline.audio.src)} />}
			<ShotScene shot={shot} f={f} fps={timeline.fps} />
			{!registry.locations[shot.location].showsText && <Captions pages={shot.captions} frame={f} />}
		</AbsoluteFill>
	);
};
