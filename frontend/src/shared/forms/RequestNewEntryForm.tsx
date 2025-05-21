import Label from 'shared/components/Label';
import Input from 'shared/components/Input';
import { useState } from 'react';
import { api } from 'api';

export default function RequestNewEntryForm() {
    const [title, setTitle] = useState('');
    const submitRequestNewEntryForm = (e: React.FormEvent) => {
        e.preventDefault();
        api.requestNewEntry(title);
    }
    return (
        <form onSubmit={(e) => submitRequestNewEntryForm(e)}>
            <Label htmlFor="title">Request New Entry for:</Label>
            <Input id="title" name="title" type="text"value={title} onChange={(e) => setTitle(e.target.value)} disabled={false} />
            <button type="submit">Submit</button>
        </form>
    );
}