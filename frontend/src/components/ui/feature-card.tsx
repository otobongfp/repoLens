/**
 * RepoLens Frontend - Feature-Card Component
 * 
 * Copyright (C) 2024 RepoLens Contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import * as React from 'react';

import { cn } from '@/lib/utils';

interface FeatureCardProps extends React.ComponentProps<'div'> {
  color?: string;
}

function FeatureCard({ className, color, ...props }: FeatureCardProps) {
  return (
    <div
      data-slot='color-card'
      className={cn(
        `text-card-foreground bg-card flex flex-col gap-6 rounded-xl border py-6 shadow-sm`,
        className,
      )}
      {...props}
    />
  );
}

function FeatureCardHeader({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot='color-card-header'
      className={cn(
        '@container/color-card-header has-data-[slot=color-card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6 grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6',
        className,
      )}
      {...props}
    />
  );
}

function FeatureCardTitle({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot='color-card-title'
      className={cn('font-semibold leading-none', className)}
      {...props}
    />
  );
}

function FeatureCardDescription({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot='color-card-description'
      className={cn('text-muted-foreground text-sm', className)}
      {...props}
    />
  );
}

function FeatureCardAction({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot='color-card-action'
      className={cn(
        'col-start-2 row-span-2 row-start-1 self-start justify-self-end',
        className,
      )}
      {...props}
    />
  );
}

function FeatureCardContent({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot='color-card-content'
      className={cn('px-6', className)}
      {...props}
    />
  );
}

function FeatureCardFooter({
  className,
  ...props
}: React.ComponentProps<'div'>) {
  return (
    <div
      data-slot='color-card-footer'
      className={cn('[.border-t]:pt-6 flex items-center px-6', className)}
      {...props}
    />
  );
}

export {
  FeatureCard,
  FeatureCardHeader,
  FeatureCardFooter,
  FeatureCardTitle,
  FeatureCardAction,
  FeatureCardDescription,
  FeatureCardContent,
};
