<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="fahuo.aspx.cs" Inherits="fahuo" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
<div align="center" style="padding: 30px; margin: 30px; height: 305px" title=" ">
    <br />
    <asp:Label ID="Label6" runat="server" Font-Size="20pt" Text="收货地址"></asp:Label>
    <br />
    <br />
    <asp:Label ID="Label1" runat="server" Text="收货人："></asp:Label>
    <asp:TextBox ID="TextBox1" runat="server"></asp:TextBox>
    <asp:RequiredFieldValidator ID="RequiredFieldValidator1" runat="server" 
        ControlToValidate="TextBox1" ErrorMessage="RequiredFieldValidator">必填</asp:RequiredFieldValidator>
    <br />
    <asp:Label ID="Label2" runat="server" Text="联系电话:"></asp:Label>
    <asp:TextBox ID="TextBox2" runat="server"></asp:TextBox>
    <asp:RequiredFieldValidator ID="RequiredFieldValidator2" runat="server" 
        ControlToValidate="TextBox2" ErrorMessage="RequiredFieldValidator">必填</asp:RequiredFieldValidator>
    <br />
    <asp:Label ID="Label3" runat="server" Text="所在地区："></asp:Label>
    <asp:TextBox ID="TextBox3" runat="server"></asp:TextBox>
    <asp:RequiredFieldValidator ID="RequiredFieldValidator3" runat="server" 
        ControlToValidate="TextBox3" ErrorMessage="RequiredFieldValidator">必填</asp:RequiredFieldValidator>
    <br />
    <asp:Label ID="Label4" runat="server" Text="街道："></asp:Label>
    <asp:TextBox ID="TextBox4" runat="server"></asp:TextBox>
    <asp:RequiredFieldValidator ID="RequiredFieldValidator4" runat="server" 
        ControlToValidate="TextBox4" ErrorMessage="RequiredFieldValidator">必填</asp:RequiredFieldValidator>
    <br />
    <asp:Label ID="Label5" runat="server" Text="邮编："></asp:Label>
    <asp:TextBox ID="TextBox5" runat="server"></asp:TextBox>
    <asp:RequiredFieldValidator ID="RequiredFieldValidator5" runat="server" 
        ControlToValidate="TextBox5" ErrorMessage="RequiredFieldValidator">必填</asp:RequiredFieldValidator>
    <br />
    <asp:Button ID="Button1" runat="server" Text="确定" onclick="Button1_Click" />
    </div>
</asp:Content>

