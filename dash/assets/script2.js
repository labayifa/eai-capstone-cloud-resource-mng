// window.mountChainlitWidget({
//   chainlitServer: "http://localhost:8000",
// });

// window.addEventListener("chainlit-call-fn", (e) => {
//   const { name, args, callback } = e.detail;
//   if (name === "formfill") {
//     console.log(name, args);
//     dash_clientside.set_props("fieldA", {value: args.fieldA});
//     dash_clientside.set_props("fieldB", {value: args.fieldB});
//     dash_clientside.set_props("fieldC", {value: args.fieldC});
//     callback("You sent: " + args.fieldA + " " + args.fieldB + " " + args.fieldC);
//   }
// });

window.mountChainlitWidget({
  chainlitServer: "http://localhost:8000",
});

// window.addEventListener("chainlit-call-fn", (e) => {
//   const { name, args, callback } = e.detail;
//   if (name === "formfill") {
//     console.log(name, args);

//     // Update the Dash app's fields
//     document.getElementById('fieldA').value = args.fieldA;
//     document.getElementById('fieldB').value = args.fieldB;
//     document.getElementById('fieldC').value = args.fieldC;

//     // Trigger the Dash app's clientside callback
//     document.getElementById('fieldA').dispatchEvent(new Event('input'));
//     document.getElementById('fieldB').dispatchEvent(new Event('input'));
//     document.getElementById('fieldC').dispatchEvent(new Event('input'));

//     callback("File sent: " + args.fieldA + " " + args.fieldB + " " + args.fieldC);
//   }
// });
