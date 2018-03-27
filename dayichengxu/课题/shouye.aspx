<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="shouye.aspx.cs" Inherits="_Default" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
    <style type ="text/css">
   .zhong1
   {
        
       }
        .style18
        {
            width: 584px;
            height: 269px;
        }
        .style21
        {
            width: 517px;
            height: 269px;
        }
        .style22
    {
        width: 618px;
        height: 269px;
    }
    .style23
    {
        width: 554px;
        height: 313px;
    }
        </style>

</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
    <div>
    <div class="zhong1"align="center" 
            
            
            
            
            
            
            style="left: 20px; height: 74px; width:100%; background-image: url('u=109685854,49878772&amp;fm=21&amp;gp=0.jpg');">
    <asp:Label ID="Label1" runat="server" Text="手机：" ForeColor="Red" 
            BorderColor="Black" Font-Size="15pt"></asp:Label>
  <%--  <asp:DropDownList ID="DropDownList1" runat="server" 
            onselectedindexchanged="DropDownList1_SelectedIndexChanged" 
            AutoPostBack="True" DataSourceID="SqlDataSource1" DataTextField="pinpai" 
            DataValueField="pinpai">
        <asp:ListItem>三星</asp:ListItem>
        <asp:ListItem>苹果</asp:ListItem>
        <asp:ListItem>华为</asp:ListItem>
        <asp:ListItem>小米</asp:ListItem>--%>
   <%-- </asp:DropDownList>--%>
    &nbsp;<asp:DropDownList ID="DropDownList1" runat="server">
            <asp:ListItem>苹果</asp:ListItem>
            <asp:ListItem>三星</asp:ListItem>
            <asp:ListItem>华为</asp:ListItem>
            <asp:ListItem>小米</asp:ListItem>
        </asp:DropDownList>
&nbsp;<asp:Button ID="Button6" runat="server" onclick="Button6_Click"   
            Text="查询" />
        &nbsp;
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      <asp:Button ID="Button3" runat="server" Text="登录" onclick="Button3_Click" /> 
    &nbsp;
        <asp:Button ID="Button5" runat="server" onclick="Button5_Click" Text="管理员登录" />
&nbsp;&nbsp;
    <asp:Button ID="Button2" runat="server" Text="注册" onclick="Button2_Click" />
    </div>
    </div>
    <div style="width: 100%" align="left" >
    <table border="1">
    <tr>
    <td class="style18" align="center" bgcolor="#FFCC99">热搜排行榜：<asp:GridView ID="GridView2" 
            runat="server" Height="282px" Width="193px" AutoGenerateColumns="False" 
            onselectedindexchanged="GridView2_SelectedIndexChanged">
        <Columns>
            <asp:BoundField DataField="pinpai" HeaderText="品牌" />
            <asp:BoundField DataField="xinghao" HeaderText="机型" />
            <asp:BoundField DataField="resouliang" HeaderText="热搜量" />
        </Columns>
        </asp:GridView>
        </td>
    <td class="style21" align="center">
        <img alt="" class="style23" src="图片/QQ图片20170228172152.jpg" /></td>
    <td class="style22" align="center" bgcolor="#FFCC99">销量排行榜：<asp:GridView ID="GridView3" 
            runat="server" Height="190px">
        </asp:GridView>
        </td>
    </tr>
    </table>
    </div>
    <div style="height: 1354px; width:100%; margin-left: 0px; margin-right: 0px;" 
        align="center">
   <%-- <table border="1" style="border-color: #000000; height: 198px;width:100%"> 
    <tr>
    <td class="style3" align="center" bgcolor="#FFFF66">
        <asp:ImageButton ID="ImageButton2" runat="server" ImageUrl="~/pingguo.jpg" 
            onclick="ImageButton2_Click" />
        iPhone，是美国苹果公司研发的智能手机， 
        它搭载iOS操作系统。</td>
     <td class="style11" align="center" bgcolor="#66FFFF">
            <asp:ImageButton ID="ImageButton1" runat="server" 
                DescriptionUrl="~/sanxing.png" ImageUrl="~/sanxing.png" 
                onclick="ImageButton1_Click" />
            三星手机，是三星集团研发的智能手机，三星手机真正开始风靡全球是从A系列开始</td></a>
    
    </tr>
    <tr>
    <td class="style6" align="center" bgcolor="#FF5050">
        <asp:ImageButton ID="ImageButton3" runat="server" Height="46px" 
            ImageUrl="~/huawei.png" onclick="ImageButton3_Click" Width="53px" />
        华为手机隶属于华为消费者业务，作为华为三大核心业务之一</td>
    <td class="style12" align="center" bgcolor="#99CCFF">
        <asp:ImageButton ID="ImageButton4" runat="server" Height="57px" 
            ImageUrl="~/xi.jpg" onclick="ImageButton4_Click" Width="59px" />
        小米手机是小米公司（全称北京小米科技有限责任公司）研发的高性能发烧级智能手机。坚持 
        “为发烧而生”的设计理念，采用线上销售模式</td>
    
    </tr>
   
    </table>--%>
        <div style="height: 303px; background-image: url('图片/0008020232552101_b.jpg');" 
            align="center">
        <asp:GridView ID="GridView4" runat="server" AutoGenerateColumns="False" 
            Height="300px" Width="100%" 
                onselectedindexchanged="GridView4_SelectedIndexChanged1" Font-Size="15px">
            <Columns>
                <asp:TemplateField HeaderText="LOGO">
                 <ItemTemplate>
<%--               <asp:Image ID="Image1" ImageUrl='<%#Eval("biaozhi") %>' runat="server">
                </asp:Image>--%>
                <br />
                 
                     <asp:Image ID="Image2" runat="server" ImageUrl='<%# Eval("biaozhi") %>' />
                 
            </ItemTemplate>
                </asp:TemplateField>
                <asp:BoundField DataField="jeisha" HeaderText="介绍" />
            </Columns>
        </asp:GridView>
    </div><div style="height: 773px">
        <asp:DataList ID="DataList1" runat="server" Height="415px" Width="100%" RepeatColumns="3" 
              style="margin-top: 21px">
        <ItemTemplate>
        <div align="center" style="width: 377px; height: 333px">
            <br />
         <%--   <asp:ImageButton ID="ImageButton5" runat="server" Height="263px" 
                ImageUrl='<%# Eval("tupian") %>' onclick="ImageButton5_Click" 
                style="margin-left: 0px" Width="226px" />--%>
                <asp:Image ID="Image1" runat="server" Height="261px" 
                ImageUrl='<%# Eval("tupian") %>' Width="246px" />
                <div align="center" style="height: 57px; width: 313px;">
                    <asp:Label ID="Label3" runat="server" Text='<%# Eval("xinghao") %>'></asp:Label>
                    <br />
<%--                    <asp:HyperLink ID="HyperLink1" runat="server" 
                        NavigateUrl='~/xiangqing.aspx?id=<%# Eval("xinghao") %>' >详情</asp:HyperLink>--%>
                        <a href="xiangqing.aspx?id=<%#Eval("xinghao") %>">详情</a>
                    <asp:Label ID="Label2" runat="server" Text='<%# Eval("jiage") %>'></asp:Label>
                    <br />
                    <asp:Button ID="Button4" runat="server" Text="加入购物车" />
            </div>
        </div>
        </div>
        </ItemTemplate>
        </asp:DataList>
    </div>
    <%--<div style="height: 1333px">
    <table style="height: 1212px; width:100%" align="center">
    <tr><td class="style24" align="center">
        &nbsp;&nbsp;&nbsp;&nbsp;
        <asp:ImageButton ID="ImageButton5" runat="server" ImageUrl="~/1799.png" />
        <br />
        小米5</td><td class="style32" align="center">
            <asp:ImageButton ID="ImageButton6" runat="server" ImageUrl="~/2088.png" />
            <br />
            苹果SE</td><td align="center">
            &nbsp;&nbsp;
            <asp:ImageButton ID="ImageButton7" runat="server" ImageUrl="~/3499.png" 
                style="margin-left: 1px" />
            <br />
            三星note5</td></tr>
        <tr><td class="style30" align="center">
            &nbsp;&nbsp;&nbsp;
            <asp:ImageButton ID="ImageButton8" runat="server" ImageUrl="~/3699.png" />
            <br />
            小米note2</td><td class="style33" align="center">
                <asp:ImageButton ID="ImageButton9" runat="server" ImageUrl="~/5999.png" />
                <br />
                小米MIX</td><td class="style25" align="center">
                &nbsp;&nbsp;&nbsp;
                <asp:ImageButton ID="ImageButton10" runat="server" ImageUrl="~/6s.png" 
                     />
                <br />
                苹果6s</td></tr>
         <tr><td class="style31" align="center">
             &nbsp;&nbsp;&nbsp;
             <asp:ImageButton ID="ImageButton11" runat="server" ImageUrl="~/7.png" 
                 Height="344px"   />
             <br />
             苹果7</td><td class="style34" align="center">
                 <asp:ImageButton ID="ImageButton12" runat="server" ImageUrl="~/mate999.png" 
                     Height="382px" />
                 <br />
                 华为mate8</td><td class="style26" align="center">
                 <asp:ImageButton ID="ImageButton13" runat="server" ImageUrl="~/w.png" 
                     Height="357px" />
                 <br />
                 三星w2017<br />
                 </td></tr>
    </table>
    </div>--%>
</asp:Content>

