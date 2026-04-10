import { DemoCard, type DemoCardData } from './DemoCard';

interface IndustryGridProps {
  demos: DemoCardData[];
}

export function IndustryGrid({ demos }: IndustryGridProps) {
  return (
    <div
      id="demos"
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
    >
      {demos.map((demo) => (
        <DemoCard key={demo.slug} {...demo} />
      ))}
    </div>
  );
}
