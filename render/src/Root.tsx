import React from 'react';
import {Composition} from 'remotion';
import {KitSheet} from './dev/KitSheet';
import {RigSheet} from './dev/RigSheet';
import {Episode} from './Episode';
import type {Timeline} from './kit/types';

// The timeline arrives through `--props` ({"timeline": ...}); this default only keeps the Studio usable.
const empty: Timeline = {schema: 'story-timeline/v1', fps: 30, width: 1920, height: 1080, durationInFrames: 1,
	series: '', episode: '', title: '', audio: {src: ''}, shots: []};

export const Root: React.FC = () => (
	<>
	<Composition id="KitSheet" component={KitSheet} durationInFrames={1} fps={30} width={1920} height={1080} />
	<Composition id="RigSheet" component={RigSheet} durationInFrames={1} fps={30} width={1920} height={1080} />
	<Composition
		id="Episode"
		component={Episode}
		defaultProps={{timeline: empty}}
		calculateMetadata={({props}) => ({
			durationInFrames: Math.max(1, props.timeline.durationInFrames),
			fps: props.timeline.fps,
			width: props.timeline.width,
			height: props.timeline.height,
		})}
	/>
	</>
);
