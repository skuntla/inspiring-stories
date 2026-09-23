import React from 'react';
import {Composition} from 'remotion';
import {Scene} from './Scene';
import {DURATION, FPS} from './timing';

export const Root: React.FC = () => (
	<Composition id="PipPoc" component={Scene} durationInFrames={DURATION} fps={FPS} width={1920} height={1080} />
);
