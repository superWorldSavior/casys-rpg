import{r as c,b as q,a6 as B,J as M,j as N,_ as m}from"./index-9ugM70_E.js";import{u as O,T as Q,r as U,g as A}from"./IconButton-2Ex1bWgf.js";const V=["addEndListener","appear","children","easing","in","onEnter","onEntered","onEntering","onExit","onExited","onExiting","style","timeout","TransitionComponent"];function p(l){return`scale(${l}, ${l**2})`}const X={entering:{opacity:1,transform:p(1)},entered:{opacity:1,transform:"none"}},h=typeof navigator<"u"&&/^((?!chrome|android).)*(safari|mobile)/i.test(navigator.userAgent)&&/(os |version\/)15(.|_)4/i.test(navigator.userAgent),Y=c.forwardRef(function(x,L){const{addEndListener:y,appear:_=!0,children:f,easing:T,in:R,onEnter:j,onEntered:w,onEntering:D,onExit:v,onExited:H,onExiting:b,style:E,timeout:o="auto",TransitionComponent:C=Q}=x,F=q(x,V),G=B(),g=c.useRef(),r=O(),u=c.useRef(null),P=M(u,f.ref,L),s=t=>e=>{if(t){const i=u.current;e===void 0?t(i):t(i,e)}},S=s(D),W=s((t,e)=>{U(t);const{duration:i,delay:d,easing:n}=A({style:E,timeout:o,easing:T},{mode:"enter"});let a;o==="auto"?(a=r.transitions.getAutoHeightDuration(t.clientHeight),g.current=a):a=i,t.style.transition=[r.transitions.create("opacity",{duration:a,delay:d}),r.transitions.create("transform",{duration:h?a:a*.666,delay:d,easing:n})].join(","),j&&j(t,e)}),$=s(w),z=s(b),J=s(t=>{const{duration:e,delay:i,easing:d}=A({style:E,timeout:o,easing:T},{mode:"exit"});let n;o==="auto"?(n=r.transitions.getAutoHeightDuration(t.clientHeight),g.current=n):n=e,t.style.transition=[r.transitions.create("opacity",{duration:n,delay:i}),r.transitions.create("transform",{duration:h?n:n*.666,delay:h?i:i||n*.333,easing:d})].join(","),t.style.opacity=0,t.style.transform=p(.75),v&&v(t)}),K=s(H),k=t=>{o==="auto"&&G.start(g.current||0,t),y&&y(u.current,t)};return N.jsx(C,m({appear:_,in:R,nodeRef:u,onEnter:W,onEntered:$,onEntering:S,onExit:J,onExited:K,onExiting:z,addEndListener:k,timeout:o==="auto"?null:o},F,{children:(t,e)=>c.cloneElement(f,m({style:m({opacity:0,transform:p(.75),visibility:t==="exited"&&!R?"hidden":void 0},X[t],E,f.props.style),ref:P},e))}))});Y.muiSupportAuto=!0;export{Y as G};
//# sourceMappingURL=Grow-DJRA9axK.js.map
