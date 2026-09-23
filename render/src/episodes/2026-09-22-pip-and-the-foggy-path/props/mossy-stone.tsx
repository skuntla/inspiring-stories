import React from 'react';
import {Stone} from '../../../kit/scenery';
import type {DrawContext, Prop} from '../../../kit/types';

// A low rounded grey stone covered in thick velvety green moss (about as tall as Wren's perch lift).
const MossyStone: React.FC<DrawContext> = () => <Stone x={0} y={0} w={170} h={60} moss />;

export const prop: Prop = {id: 'mossy-stone', width: 170, Component: MossyStone};
