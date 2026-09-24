import {makeHuman} from '../../../kit/human';
import type {Rig} from '../../../kit/types';

// The merchant from the capital: stout, a red silk turban with a jewel and a white plume, a curled
// mustache, a royal-blue knee-length coat with gold buttons, white churidar and gold slippers.
export const rig: Rig = {
	id: 'merchant',
	stances: ['stand', 'walk', 'sit', 'reach', 'hold'],
	moods: ['neutral', 'happy', 'sad', 'surprised', 'worried', 'scared', 'angry', 'thoughtful', 'proud', 'tired', 'calm'],
	height: 500,
	anchors: {hand: [90, -262], head: [8, -522]},
	Component: makeHuman({
		skin: '#c68e64', skinShade: '#a87450',
		turban: {color: '#c8323a', shade: '#9e2530', jewel: '#4fa0d8'},
		mustache: {color: '#2a1d16', curled: true}, brows: '#2a1d16', browWidth: 5,
		shirt: '#2f5d8a', shirtShade: '#244a70', sleeves: 'long', buttons: '#e9c046',
		skirt: {color: '#2f5d8a', shade: '#244a70', hem: -120},
		pants: '#f1ece0', shoes: '#d9a441', stout: true,
	}),
};
