import Title from "shared/components/Title";
import { useEffect, useState } from "react";
import Button from "shared/components/Button";
import Input from "shared/components/Input";
import Label from "shared/components/Label";
import { api } from "api";
import { User } from "shared/types/User";
import { useAuth } from "shared/context/AuthContext";

export default function UserProfile() {
    const { accessToken, userEmail, isAuthenticated, setAccessToken, setUserEmail, handleLogout, ws } = useAuth();
    const [loading, setLoading] = useState(true);
    const [editing, setEditing] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [userSlug, setUserSlug] = useState(localStorage.getItem('userSlug') || "");
    const [userProfile, setUserProfile] = useState<User | null>(null);

    useEffect(() => {  
        const fetchItem = () => {
          setLoading(true);
          api.getUser(`${userSlug}`)
            .then(res => res.json())
            .then(data => {
              if (data) {
                setUserProfile(data);
              } else {
                setError("Malformed user profile data.");
              }
              setLoading(false);
            })
            .catch(error => {
              setError(error.message);
              setLoading(false);
            });
        };
        fetchItem();
      }, [userSlug]);
    
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        if (!userProfile) return;
        setUserProfile({ ...userProfile, [name]: value });
    };

    const handleToggleEdit = () => setEditing((prev) => !prev);

    const handleSave = () => {
        // Save logic could go here (e.g., API call)
        setEditing(false);
    };

    const testNotifications = () => {
      api.testNotification(userSlug)
    };

    return (
    <>
    <Title text={userProfile?.username || ""}/>
    <div className="center-container">
        <div className="header">User Profile</div>
        <div className="content">
            <div>
            <Label htmlFor="firstName">First Name</Label>
            <Input
                id="firstName"
                name="firstName"
                value={userProfile?.first_name ?? ""}
                onChange={handleChange}
                disabled={!editing}
            />
            </div>

            <div>
            <Label htmlFor="lastName">Last Name</Label>
            <Input
                id="lastName"
                name="lastName"
                value={userProfile?.last_name ?? ""}
                onChange={handleChange}
                disabled={!editing}
            />
            </div>

            <div>
            <Label htmlFor="username">Username</Label>
            <Input
                id="username"
                name="username"
                value={userProfile?.username ?? ""}
                onChange={handleChange}
                disabled={!editing}
            />
            </div>
            <div className="flex justify-end gap-4">
                {editing ? (
                <>
                    <Button className="save" onClick={handleSave}>Save</Button>
                    <Button className="cancel" onClick={handleToggleEdit}>
                    Cancel
                    </Button>
                </>
                ) : (
                <Button onClick={handleToggleEdit}>Edit</Button>
                )}
            </div>
            <ul>
                <li><strong>Access Token: </strong>{accessToken}</li>
                <li><strong>Email: </strong>{userEmail}</li>
                <li><strong>Name: </strong>{userProfile?.username}</li>
                <li><strong>Slug: </strong>{userSlug}</li>
            </ul>
            <Button onClick={testNotifications}>Test Notifications</Button>
            <Button onClick={handleLogout}>Logout</Button>
        </div>
    </div>
    </>
    );
}