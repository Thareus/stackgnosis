export default function Label({ htmlFor, children, className }: { htmlFor: string; className?: string; children: React.ReactNode; }) {
    return (
      <label htmlFor={htmlFor} className={className}>
        {children}
      </label>
    );
  }