import React from 'react';
import {AbsoluteFill} from 'remotion';
import {registry} from '../generated/registry';
import {ATMOSPHERE} from '../kit/atmosphere';
import {Defs, Sky, palette} from '../kit/style';
import type {Location, TimeOfDay} from '../kit/types';

// Dev only: every location in the current registry at morning and night, then every atmosphere
// overlay over the first location, each tile a scaled-down full scene.
const Tile: React.FC<{loc: Location; time: TimeOfDay; atmosphere?: string; x: number; y: number; label: string}> = ({loc, time, atmosphere, x, y, label}) => {
	const pal = palette(time);
	const ctx = {t: 2, palette: pal, timeOfDay: time};
	const A = atmosphere ? ATMOSPHERE[atmosphere] : undefined;
	return (
		<g transform={`translate(${x} ${y})`}>
			<svg width={300} height={169} viewBox="0 0 1920 1080">
				<Defs palette={pal} />
				{!loc.interior && <Sky palette={pal} />}
				<loc.Background {...ctx} />
				{A && <A t={2} palette={pal} layer="back" />}
				{loc.Foreground && <loc.Foreground {...ctx} />}
				{A && <A t={2} palette={pal} layer="front" />}
				<rect width={1920} height={1080} fill={pal.tint} opacity={pal.tintOpacity} style={{mixBlendMode: 'multiply'}} />
			</svg>
			<text x={4} y={186} fontSize={15} fontFamily="system-ui" fill="#3b2a20">{label}</text>
		</g>
	);
};

export const KitSheet: React.FC = () => {
	const locs = Object.values(registry.locations);
	const tiles: React.ReactNode[] = [];
	let n = 0;
	const place = (node: (x: number, y: number) => React.ReactNode) => {
		tiles.push(<React.Fragment key={n}>{node(12 + (n % 6) * 318, 12 + Math.floor(n / 6) * 200)}</React.Fragment>);
		n++;
	};
	for (const loc of locs) for (const time of ['morning', 'night'] as TimeOfDay[])
		place((x, y) => <Tile loc={loc} time={time} x={x} y={y} label={`${loc.id} / ${time}`} />);
	for (const a of Object.keys(ATMOSPHERE))
		place((x, y) => <Tile loc={locs[0]} time="dusk" atmosphere={a} x={x} y={y} label={`${a} (dusk)`} />);
	return (
		<AbsoluteFill style={{backgroundColor: '#efe7d4'}}>
			<svg viewBox="0 0 1920 1080" width="100%" height="100%">{tiles}</svg>
		</AbsoluteFill>
	);
};
