import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame} from 'remotion';
import {registry} from './generated/registry';
import {ATMOSPHERE} from './kit/atmosphere';
import {Captions} from './kit/Captions';
import {Defs, Sky, ease, palette} from './kit/style';
import type {CastMember, DrawContext, Shape, Shot, Timeline, View} from './kit/types';

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

const view = (shot: Shot, f: number): View => {
	const e = ease(Math.min(1, f / Math.max(1, shot.frames - 1)));
	const [a, b] = [shot.camera.from, shot.camera.to];
	return [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e, a[2] + (b[2] - a[2]) * e];
};

const ShotScene: React.FC<{shot: Shot; f: number; fps: number}> = ({shot, f, fps}) => {
	const location = registry.locations[shot.location];
	const pal = palette(shot.timeOfDay);
	const ctx: DrawContext = {t: f / fps, palette: pal, timeOfDay: shot.timeOfDay};
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
					const mouth = mouthAt(c, f);
					const prop = held.get(c.id);
					const P = prop ? registry.props[prop] : undefined;
					return (
						<g key={c.id} transform={`translate(${c.x} ${ground}) scale(${flip * c.depth} ${c.depth})`}>
							<rig.Component {...ctx} stance={c.stance} mood={c.mood} mouth={mouth} eye={eyeAt(c, f)}
								speaking={mouth !== 'rest'} facing={c.facing} />
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
			<Captions pages={shot.captions} frame={f} />
		</AbsoluteFill>
	);
};
