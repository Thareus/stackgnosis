interface TitleProps {
  text: string;
};

const Title = ({text}:TitleProps) => (
  <div className="header title glass-shimmer">
    <h1>{text}</h1>
  </div>
);

export default Title;