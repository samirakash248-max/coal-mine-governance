import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

type StatusVariant = 'healthy' | 'warning' | 'elevated' | 'critical' | 'info' | 'inactive';

interface StatusBadgeProps {
  variant: StatusVariant;
  children: React.ReactNode;
  size?: 'sm' | 'md';
  dot?: boolean; // show colored dot before text
  className?: string;
}

const variantStyles: Record<StatusVariant, string> = {
  healthy: 'bg-green-50 text-green-700 border-green-200',
  warning: 'bg-amber-50 text-amber-700 border-amber-200',
  elevated: 'bg-orange-50 text-orange-700 border-orange-200',
  critical: 'bg-red-50 text-red-700 border-red-200',
  info: 'bg-primary-50 text-primary-700 border-primary-200',
  inactive: 'bg-gray-50 text-gray-600 border-gray-200',
};

const dotStyles: Record<StatusVariant, string> = {
  healthy: 'bg-green-500',
  warning: 'bg-amber-500',
  elevated: 'bg-orange-500',
  critical: 'bg-red-500',
  info: 'bg-primary-500',
  inactive: 'bg-gray-400',
};

export function StatusBadge({ variant, children, size = 'md', dot = false, className }: StatusBadgeProps) {
  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 rounded-full border font-medium',
          size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm',
          variantStyles[variant]
        ),
        className
      )}
    >
      {dot && (
        <span className={clsx('inline-block h-1.5 w-1.5 rounded-full', dotStyles[variant])} />
      )}
      {children}
    </span>
  );
}
