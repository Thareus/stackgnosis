import Title from "shared/components/Title";

const EntryNotFound = () => {
  return (
    <>
      <Title text="Entry not Found"/>
      <div className="entry-container">
        <div id="entry-content" className="header">
          <h3>
            We could not find this entry.
          </h3>
        </div>
      </div>
    </>
  );
};

export default EntryNotFound;