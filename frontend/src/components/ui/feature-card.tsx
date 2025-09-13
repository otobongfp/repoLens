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
