/**
 * Unified user avatar component
 * Gmail-like account avatar with warm, muted styling
 */

interface UserAvatarProps {
  size?: 'sm' | 'md' | 'lg';
  initial?: string;
}

export function UserAvatar({ size = 'md', initial = 'D' }: UserAvatarProps) {
  const sizeClasses = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-10 h-10 text-base',
  };

  return (
    <div
      className={`${sizeClasses[size]} rounded-full bg-[#8B7355] border border-[rgba(255,255,255,0.08)] flex items-center justify-center font-medium text-[#F5F5F4] flex-shrink-0`}
      aria-label="User account"
    >
      {initial}
    </div>
  );
}
