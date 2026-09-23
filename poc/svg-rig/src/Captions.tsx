import React from 'react';
import {lineAt} from './timing';

const PAGE = 7; // words shown at once

/** Word-level captions: the current page of words, with the spoken word highlighted. */
export const Captions: React.FC<{seconds: number}> = ({seconds}) => {
	const line = lineAt(seconds);
	if (!line || line.words.length === 0) return null;
	let current = line.words.findIndex((w) => seconds >= w.start && seconds < w.end);
	if (current < 0) current = line.words.filter((w) => w.end <= seconds).length - 1;
	if (current < 0) return null;
	const pageStart = Math.floor(current / PAGE) * PAGE;
	const page = line.words.slice(pageStart, pageStart + PAGE);
	return (
		<div
			style={{
				position: 'absolute',
				bottom: 40,
				width: '100%',
				display: 'flex',
				justifyContent: 'center',
			}}
		>
			<div
				style={{
					background: 'rgba(40, 34, 26, 0.55)',
					borderRadius: 18,
					padding: '14px 28px',
					fontFamily: 'Georgia, "Times New Roman", serif',
					fontSize: 50,
					fontStyle: line.speaker === 'narrator' ? 'italic' : 'normal',
					textAlign: 'center',
					color: '#f7f1e4',
					letterSpacing: 0.5,
				}}
			>
				{line.speaker !== 'narrator' && (
					<span style={{display: 'block', fontFamily: 'system-ui, sans-serif', fontWeight: 700, fontSize: 22,
						letterSpacing: 4, textTransform: 'uppercase', color: '#f3a54f', textAlign: 'center'}}>
						{line.speaker}
					</span>
				)}
				{page.map((w, i) => {
					const active = pageStart + i === current && seconds < w.end + 0.05;
					return (
						<span key={i} style={{color: active ? '#ffd98a' : '#f7f1e4', marginRight: 14}}>
							{w.text}
						</span>
					);
				})}
			</div>
		</div>
	);
};
