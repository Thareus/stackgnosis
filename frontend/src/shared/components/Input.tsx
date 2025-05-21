export default function Input({ id, name, value, onChange, disabled, type }: { id: string; name: string; value: string; onChange: (e: React.ChangeEvent<HTMLInputElement>) => void; disabled: boolean; type?: string }) {
    return (
      <input
        id={id}
        name={name}
        type={type} 
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 disabled:bg-gray-100"
      />
    );
  }