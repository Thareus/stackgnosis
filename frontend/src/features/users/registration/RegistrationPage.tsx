import RegisterForm from "./RegisterForm";
import Title from "shared/components/Title";

const RegistrationPage = () => {
  return (
    <>
    <Title text="Register"/>
    <div className="center-container">
        <div className="content">
            <RegisterForm />
        </div>
    </div>
    </>
  );
};

export default RegistrationPage;