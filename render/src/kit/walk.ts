// A shared planted-foot walk cycle. Each foot spends half the cycle on the ground (stance), sliding
// back relative to the body at exactly the walking speed, so in the world it stays put; the other
// half it lifts and swings forward (swing). The body bobs up at each mid-stance.

export const CADENCE = 5.4; // rad/s when stepping on the spot: one full cycle (two steps) takes about 1.16 s
export const MIN_CADENCE = 3.2; // rad/s: the slowest natural cycle (about 2 s for two steps)

export type WalkFrame = {
	feet: [[number, number], [number, number]]; // [dx, dy] offsets for the near and far foot
	bob: number; // vertical body offset (negative is up)
	swing: number; // -1..1, for arms swinging opposite the legs
};

const TAU = Math.PI * 2;

/**
 * speed: px/s in the rig's own drawing units (0 = stepping on the spot).
 * maxStride: largest half-stride in px; lift: foot lift at mid-swing; bobHeight: body rise at mid-stance.
 */
export const walkCycle = (t: number, speed: number, maxStride = 34, lift = 16, bobHeight = 6): WalkFrame => {
	// Prefer a full stride and let the cadence follow the speed (stance covers 2a in pi / w seconds);
	// below MIN_CADENCE shorten the stride instead, so slow walks do not turn into slow motion.
	let a = maxStride;
	let w = (speed * Math.PI) / (2 * a);
	if (w < MIN_CADENCE) {
		w = speed > 0 ? MIN_CADENCE : CADENCE;
		a = (speed * Math.PI) / (2 * w);
	}
	const phase = t * w;
	const foot = (ph: number): [number, number] => {
		const p = ((ph % TAU) + TAU) % TAU;
		if (p < Math.PI) return [a - 2 * a * (p / Math.PI), 0];
		const q = (p - Math.PI) / Math.PI;
		const eased = (1 - Math.cos(q * Math.PI)) / 2;
		return [-a + 2 * a * eased, -lift * Math.sin(q * Math.PI)];
	};
	return {
		feet: [foot(phase), foot(phase + Math.PI)],
		bob: -bobHeight * Math.pow(Math.sin(phase), 2),
		swing: Math.cos(phase),
	};
};

/** Two-bone IK: the middle joint for a root and end point. Knees bend forward (+x, dir 1);
 * elbows bend backward (dir -1). */
export const knee = (hip: [number, number], foot: [number, number], upper: number, lower: number, dir: 1 | -1 = 1): [number, number] => {
	const dx = foot[0] - hip[0];
	const dy = foot[1] - hip[1];
	const d = Math.min(Math.hypot(dx, dy), upper + lower - 0.01);
	const a = (upper * upper - lower * lower + d * d) / (2 * d); // distance from hip along the hip->foot line
	const h = Math.sqrt(Math.max(0, upper * upper - a * a));
	const ux = dx / (d || 1);
	const uy = dy / (d || 1);
	// perpendicular pointing forward (+x)
	const px = (uy > 0 ? uy : -uy) * dir;
	const py = (uy > 0 ? -ux : ux) * dir;
	return [hip[0] + ux * a + px * h, hip[1] + uy * a + py * h];
};
