<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="xiaomi.aspx.cs" Inherits="xiaomi" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
<div align="center">
    <asp:GridView ID="GridView1" runat="server" AutoGenerateColumns="False" 
        BorderColor="White">
        <Columns>
            <asp:TemplateField HeaderText="图片">
            <ItemTemplate>
               <asp:Image ID="Image1" ImageUrl='<%#Eval("zhaopian") %>' runat="server">
                </asp:Image>
                <br />
                <asp:Button ID="Button1" runat="server" Text="购买" />
            </ItemTemplate></asp:TemplateField>
            <asp:BoundField DataField="canshu" HeaderText="参数" />
            <asp:BoundField DataField="jiage" HeaderText="价格" />
        </Columns>
    </asp:GridView></div>
</asp:Content>

