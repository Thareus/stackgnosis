import LoginForm from "./LoginForm";
import Title from "shared/components/Title";

function LoginPage() {
  return (
    <>
    <Title text="Login"/>
    <div className="center-container">
        <div className="content">
            <LoginForm/>
        </div>
    </div>
    </>
  );
};

export default LoginPage;