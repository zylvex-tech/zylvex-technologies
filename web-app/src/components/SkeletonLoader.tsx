interface SkeletonLoaderProps {
  className?: string;
  lines?: number;
}

export default function SkeletonLoader({ className = '', lines = 1 }: SkeletonLoaderProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={`shimmer rounded-lg ${i === 0 ? 'h-4 w-3/4' : i % 2 === 0 ? 'h-3 w-full' : 'h-3 w-5/6'}`}
        />
      ))}
    </div>
  );
}
